# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xmlrpclib
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

REFUND = ('invoice/refund')


class PrintAccountInvoiceWizard(models.TransientModel):
    _inherit = 'print.account.invoice.wizard'

    state_sign = fields.Char(
        default=lambda self: self._get_default_state('state_sign'),
        readonly=True,
    )
    state = fields.Char(
        default=lambda self: self._get_default_state('state'),
        readonly=True,
    )
    # TODO: How can we do this product or service
    reason_dcn_code = fields.Selection([
        ('CDNG01', 'ลดราคาสินค้าที่ขาย (สินค้าผิดข้อกำหนดที่ตกลงกัน)'),
        ('CDNG02', 'สินค้าชำรุดเสียหาย'),
        ('CDNG03', 'สินค้าขาดจำนวนตามที่ตกลงซื้อขาย'),
        ('CDNG04', 'คำนวณราคาสินค้าผิดพลาดสูงกว่าที่เป็นจริง'),
        ('CDNG05', 'รับคืนสินค้า (ไม่ตรงตามคำพรรณนา)'),
        ('CDNG99', 'เหตุอื่น (ระบุสาเหตุ)')],
        string="Reason for Debit/Credir Note"
    )
    reason_inv_code = fields.Selection([
        ('DBNG01','มีการเพิ่มราคาค่าสินค้า (สินค้าเกินกว่าจำนวนที่ตกลงกัน)'),
        ('DBNG02','คำนวณราคาสินค้า ผิดพลาดต่ำกว่าที่เป็นจริง'),
        ('DBNG99','เหตุอื่นๆ (ระบุสาเหตุ)')],
        string="Reason for update",
    )
    reason_text = fields.Text()

    @api.multi
    def _get_default_state(self, state):
        active_ids = self._context.get('active_ids')
        invoice_ids = self.env['account.invoice'].browse(active_ids)
        state = invoice_ids.mapped(state)
        if len(set(state)) > 1:
            raise ValidationError(_("Selected Document state more than 1"))
        return state and state[0] or False

    @api.multi
    def _connect_docsign_server(self):
        self.ensure_one()
        company_id = self.env.user.company_id
        url = company_id.pabietax_web_url_test or company_id.pabietax_web_url
        db = company_id.pabietax_db
        username = company_id.pabietax_user
        password = company_id.pabietax_password
        # connect with docsign server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/common'.format(url))
        try:
            uid = models.authenticate(db, username, password, {})
            if not uid:
                raise ValidationError(_(
                    'Login server error, Please check username and password.'))
            models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))
            return db, password, uid, models
        except Exception as e:
            raise ValidationError(_("%s" % e))

    @api.multi
    def _check_refund_direct(self, refund_ids):
        self.ensure_one()
        direct_refund = refund_ids.filtered(lambda l: not l.origin_invoice_id)
        not_preprint = refund_ids.filtered(lambda l: not l.number_preprint)
        # create from mySale
        if direct_refund:
            refund_number = ", ".join(direct_refund.mapped('number'))
            raise ValidationError(_(
                "%s don't have origin invoice" % refund_number))
        if not_preprint:
            raise ValidationError(_(
                "Some Credit Note don't have Preprint Number."))

    @api.multi
    def _check_origin_invoice(self, refund_id):
        self.ensure_one()
        Voucher = self.env['account.voucher']
        move_ids = \
            refund_id.origin_invoice_id.payment_ids.mapped('move_id')._ids
        voucher_ids = Voucher.search([('move_id', 'in', move_ids)])
        voucher_not_sign = \
            voucher_ids.filtered(lambda l: l.state_sign == 'waiting')
        if voucher_not_sign:
            raise ValidationError(_(
                "%s is not sign." % voucher_not_sign.number))
        preprint = ", ".join(voucher_ids.mapped('number_preprint'))
        return preprint

    @api.multi
    def _prepare_invoice(self, invoice_ids):
        self.ensure_one()
        invoice_dict = []
        reason = ""
        reason_text = ""
        cancel_form = self._context.get("cancel_sign", False)
        if cancel_form and invoice_ids.filtered(lambda l: l.state != 'cancel'):
            raise ValidationError(_("State document is not cancel."))
        if self.doc_print in REFUND:
            if self.doctype == 'out_refund':
                self._check_refund_direct(invoice_ids)
                doctype = cancel_form and 'T07' or '81' # credit note
                reason = self.reason_dcn_code
                if self.reason_dcn_code == 'CDNG99':
                    reason_text = self.reason_text
            elif self.doctype == 'out_invoice':
                doctype = cancel_form and 'T07' or '380'
                reason = self.reason_inv_code
                if self.reason_inv_code == 'DBNG99':
                    reason_text = self.reason_text
        else:
            raise ValidationError(_("This Form can't sign."))
        # seller by company
        seller = self.env.user.company_id.partner_id
        for invoice in invoice_ids:
            # refund
            if invoice.origin_invoice_id:
                origin = self._check_origin_invoice(invoice)
            else:
                origin = cancel_form and invoice.number_preprint or False
            # invoice lines
            line_ids = [(0, 0, {
                'name': line.name,
                'quantity': line.quantity,
                # 'uom': line,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'product_code': line.product_id.default_code,
                'product_name': line.product_id.name,
                'taxes': line.invoice_line_tax_id.name,
                'taxes_percent':
                    round(line.invoice_line_tax_id.amount*100, 2),
                }) for line in invoice.invoice_line]
            # create invoice printing document
            invoice_dict.append({
                # header
                'doctype': doctype,
                'docform': self.doc_print,
                'lang_form': self.lang,
                'number': invoice.number_preprint or invoice.id,  # TODO: number preprint CN
                'customer_code': invoice.partner_id.search_key,
                'customer_name': invoice.partner_id.name,
                'seller_name': seller.name,
                'currency': invoice.currency_id.name,
                'date_document': invoice.date_invoice or invoice.date_document,
                'create_document': invoice.date_document,
                'operating_unit': invoice.operating_unit_id.name,
                'payment_term': invoice.payment_term.note,
                'purpose_code': reason,
                'purpose_reason_other': reason_text,
                'notes': invoice.comment,
                # customer information
                'customer_street': invoice.partner_id.street,
                'customer_street2': invoice.partner_id.street2,
                'customer_city': '',
                'customer_state': '',
                'customer_zip': invoice.partner_id.zip,
                'customer_country_code':
                    invoice.partner_id.country_id.code or 'TH',
                'customer_vat': invoice.partner_id.vat,
                'customer_phone':
                    invoice.partner_id.phone or invoice.partner_id.mobile,
                'customer_email': invoice.partner_id.email,
                'customer_taxbranch_code': invoice.partner_id.taxbranch,
                'customer_taxbranch_name': 'สำนักงานใหญ่',
                # seller information
                'seller_street': seller.street,
                'seller_street2': seller.street2,
                'seller_city': '',
                'seller_state': '',
                'seller_zip': seller.zip,
                'seller_country_code': seller.country_id.code or 'TH',
                'seller_vat': seller.vat,
                'seller_phone': seller.phone or seller.mobile,
                'seller_fax': seller.fax,
                'seller_email': seller.email,
                'seller_taxbranch_code': seller.taxbranch or '00000',
                'seller_taxbranch_name': 'สำนักงานใหญ่',
                'amount_untaxed': invoice.amount_untaxed,
                'amount_tax': invoice.amount_tax,
                'amount_total': invoice.amount_total,
                # origin
                'system_origin_name': 'pabi2',
                'system_origin_number': invoice.number or invoice.id,
                'origin_id': origin,
                'user_sign': self.env.user.name,
                'validate_by': invoice.validate_user_id.name,
                'approved_by': self.env.user.name,  # TODO: Waiting new pg.
                # lines
                'printing_lines': line_ids,
            })
        return invoice_dict

    @api.multi
    def _create_attachment(self, res_ids):
        self.ensure_one()
        invoice_obj = self.env['account.invoice']
        attachment_obj = self.env['ir.attachment']
        invoice_ids = self.env['account.invoice']
        for res in res_ids:
            if res['status'] == 'OK':
                preview = self._context.get('preview')
                state_draft = self._context.get('draft')
                domain = [('number', '=', res['name'])]
                if state_draft:
                    domain = [('id', '=', res['name'])]
                invoice_id = invoice_obj.search(domain)
                # unlink preview pdf
                filename = _('%s_preview.pdf') % res['preprint_number']
                name_preview = attachment_obj.search([('name', '=', filename)])
                if name_preview:
                    name_preview.unlink()
                if not preview:
                    filename = _('%s.pdf') % res['preprint_number']
                # create url attachment
                attachment_obj.create({
                    'name': filename,
                    'type': 'url',
                    'url': res['link_download'],
                    'res_model': invoice_id._name,
                    'res_id': invoice_id.id,
                })
                invoice_ids |= invoice_id
            # elif res['status'] == 'FAILE':
            else:
                raise ValidationError(_("%s" % res['errorMessage']))
        return invoice_ids

    @api.multi
    def _stamp_invoice_pdf(self, invoice_dict, models, db, uid, password):
        cancel_form = self._context.get("cancel_sign", False)
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'action_call_service', [invoice_dict])
        invoice_ok = self._create_attachment(res_ids)
        state = 'signed'
        if cancel_form:
            state = 'cancel'
        invoice_ok.write({'state_sign': state})
        return True

    @api.multi
    def _check_edit_value(self, invoice_dict, models, db, uid, password):
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'check_edit_value', [invoice_dict])
        for res in res_ids:
            if res['status'] == 'ER':
                raise ValidationError(_("%s" % res['errorMessage']))

    @api.multi
    def action_sign_account_invoice(self):
        edit_sign = self._context.get("edit_sign", False)
        # connect with server
        db, password, uid, models = self._connect_docsign_server()
        # Prepare Invoice
        active_ids = self._context.get('active_ids')
        invoice_ids = self.env['account.invoice'].browse(active_ids)
        if invoice_ids.filtered(lambda l: l.state == 'draft'):
            raise ValidationError(_("State draft can not sign."))
        invoice_dict = self._prepare_invoice(invoice_ids)
        # call method in server
        if edit_sign:
            self._check_edit_value(invoice_dict, models, db, uid, password)
        self._stamp_invoice_pdf(invoice_dict, models, db, uid, password)
        return True

    @api.multi
    def action_preview_account_invoice(self):
        ctx = self._context.copy()
        # connect with server
        db, password, uid, models = self._connect_docsign_server()
        # Prepare Invoice
        active_ids = self._context.get('active_ids')
        invoice_ids = self.env['account.invoice'].browse(active_ids)
        invoice_dict = self._prepare_invoice(invoice_ids)
        ctx.update({'preview': True})
        if invoice_ids.filtered(lambda l: l.state == 'draft'):
            ctx.update({'draft': True})
        # call method in server
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'generate_pdf_file_link', [invoice_dict])
        self.with_context(ctx)._create_attachment(res_ids)
        return True
