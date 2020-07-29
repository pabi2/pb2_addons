# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xmlrpclib
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

RECEIPT = ('customer_receipt')
TAX_RECEIPT = ('customer_tax_receipt', 'customer_tax_receipt200')


class PrintAccountVoucherWizard(models.TransientModel):
    _inherit = 'print.account.voucher.wizard'

    state_sign = fields.Selection([
        ('waiting', 'Waiting'),
        ('signed', 'Signed'), ],
        string="State Sign",
        default=lambda self: self._get_default_state(),
        readonly=True,
    )
    reason_tax_receipt_update = fields.Selection([
        ('TIVC01', 'ชื่อผิด'),
        ('TIVC02', 'ที่อยู่ผิด'),
        ('TIVC99', 'เหตุอื่น (ระบุสาเหตุ)'), ],
    )
    reason_receipt_update = fields.Selection([
        ('RCTC01', 'ชื่อผิด'),
        ('RCTC02', 'ที่อยู่ผิด'),
        ('RCTC03', 'รับคืนสินค้า / '\
            'ยกเลิกบริการ ทั้งจำนวน (ระบุจำนวนเงิน) บาท'),
        ('RCTC04', 'รับคืนสินค้า / ยกเลิกบริการ '\
            'บางส่วนจำนวน (ระบุจำนวนเงิน) บาท'),
        ('RCTC99', 'เหตุอื่น (ระบุสาเหตุ)'), ],
    )
    reason_text = fields.Text()

    @api.multi
    def _get_default_state(self):
        active_ids = self._context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(active_ids)
        state = voucher_ids.mapped('state_sign')
        if len(set(state)) > 1:
            raise ValidationError(_("Selected Document state more than 1"))
        return state and state[0] or False

    @api.multi
    def _connect_docsign_server(self, url, db, username, password):
        self.ensure_one()
        # connect with docsign server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/common'.format(url))
        try:
            uid = models.authenticate(db, username, password, {})
            if not uid:
                raise ValidationError(_(
                    'Login server error, Please check username and password.'))
            return uid
        except Exception as e:
            raise ValidationError(_("%s" % e))

    @api.multi
    def _prepare_voucher(self, voucher_ids):
        self.ensure_one()
        voucher_dict = []
        reason = ""
        reason_text = ""
        doctype = ""
        # seller by company
        seller = self.env.user.company_id.partner_id
        if voucher_ids.filtered(lambda l: not l.number_preprint):
            raise ValidationError(_("Pre-print Number is null."))
        if self.doc_print in TAX_RECEIPT:
            doctype = 'T03'
            reason = self.reason_tax_receipt_update
            if self.reason_tax_receipt_update == 'TIVC99':
                reason_text = self.reason_text
        elif self.doc_print in RECEIPT:
            doctype = 'T01'
            reason = self.reason_receipt_update
            if self.reason_receipt_update == 'RCTC99':
                reason_text = self.reason_text
        else:
            raise ValidationError(_("This Form can't sign."))
        for voucher in voucher_ids:
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
            # invoice lines
            line_ids = []
            for voucher_line in voucher.line_ids:
                invoice_id = voucher_line.invoice_id
                line_ids.extend([(0, 0, {
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
                    }) for line in invoice_id.invoice_line])
                amount_untaxed += invoice_id.amount_untaxed
                amount_tax += invoice_id.amount_tax
                amount_total += invoice_id.amount_total
            # payment diff
            diff_line_ids = [(0, 0, {
                'note': diff.note,
                'amount': diff.amount,
            }) for diff in voucher.multiple_reconcile_ids]
            # create invoice printing document
            voucher_dict.append({
                # header
                'doctype': doctype,
                'docform': self.doc_print,
                'lang_form': self.lang,
                'number': voucher.number_preprint,
                'customer_code': voucher.partner_id.search_key,
                'customer_name': voucher.partner_id.name,
                'seller_name': seller.name,
                'currency': voucher.currency_id.name,
                'date_document': voucher.date_document,
                'operating_unit': voucher.operating_unit_id.name,
                'purpose_code': reason,
                'purpose_reason_other': reason_text,
                'notes': voucher.narration,
                # customer information
                'customer_street': voucher.partner_id.street,
                'customer_street2': voucher.partner_id.street2,
                'customer_city': '',
                'customer_state': '',
                'customer_zip': voucher.partner_id.zip,
                'customer_country_code':
                    voucher.partner_id.country_id.code or 'TH',
                'customer_vat': voucher.partner_id.vat,
                'customer_phone':
                    voucher.partner_id.phone or voucher.partner_id.mobile,
                'customer_email': voucher.partner_id.email,
                'customer_taxbranch_code': voucher.partner_id.taxbranch,
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
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
                # origin
                'system_origin_name': 'pabi2',
                'system_origin_number': voucher.number,
                'user_sign': self.env.user.name,
                'approved_by': self.env.user.name,  # TODO: Waiting new pg.
                # payment method
                'payment_method': voucher.receipt_type,
                'check_no': voucher.number_cheque,
                'check_date':
                voucher.number_cheque and voucher.date_cheque or False,
                'bank_name':
                voucher.number_cheque and voucher.bank_cheque or False,
                'bank_branch':
                voucher.number_cheque and voucher.bank_branch or False,
                'rdx_no': '',  # TODO: Waiting RDX
                # lines
                'printing_lines': line_ids,
                'payment_diff_lines': diff_line_ids,
            })
        return voucher_dict

    @api.multi
    def _create_attachment(self, res_ids):
        self.ensure_one()
        voucher_obj = self.env['account.voucher']
        attachment_obj = self.env['ir.attachment']
        voucher_ids = self.env['account.voucher']
        for res in res_ids:
            if res['status'] == 'OK':
                preview = self._context.get('preview')
                voucher_id = voucher_obj.search([('number', '=', res['name'])])
                # unlink preview pdf
                filename = _('%s_preview.pdf') % res['name']
                name_preview = attachment_obj.search([('name', '=', filename)])
                if name_preview:
                    name_preview.unlink()
                if not preview:
                    filename = _('%s.pdf') % res['name']
                # create url attachment
                attachment_obj.create({
                    'name': filename,
                    'type': 'url',
                    'url': res['link_download'],
                    'res_model': voucher_id._name,
                    'res_id': voucher_id.id,
                })
                voucher_id.write({
                    'number_preprint_current': res['preprint_number']
                })
                voucher_ids |= voucher_id
            else:
                raise ValidationError(_("%s" % res['errorMessage']))
        return voucher_ids

    @api.multi
    def _stamp_voucher_pdf(self, voucher_dict, models, db, uid, password):
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'action_call_service', [voucher_dict])
        voucher_ok = self._create_attachment(res_ids)
        voucher_ok.write({'state_sign': 'signed'})
        return True

    @api.multi
    def _check_edit_value(self, voucher_dict, models, db, uid, password):
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'check_edit_value', [voucher_dict])
        for res in res_ids:
            if res['status'] == 'ER':
                raise ValidationError(_("%s" % res['errorMessage']))

    @api.multi
    def action_sign_account_voucher(self):
        url = self.env.user.company_id.pabietax_web_url
        db = self.env.user.company_id.pabietax_db
        username = self.env.user.company_id.pabietax_user
        password = self.env.user.company_id.pabietax_password
        edit_sign = self._context.get("Edit_sign", False)
        # connect with server
        uid = self._connect_docsign_server(url, db, username, password)

        active_ids = self._context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(active_ids)
        # call method in server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))
        voucher_dict = self._prepare_voucher(voucher_ids)
        if edit_sign:
            self._check_edit_value(voucher_dict, models, db, uid, password)
        self._stamp_voucher_pdf(voucher_dict, models, db, uid, password)
        return True

    @api.multi
    def action_preview_account_voucher(self):
        url = self.env.user.company_id.pabietax_web_url
        db = self.env.user.company_id.pabietax_db
        username = self.env.user.company_id.pabietax_user
        password = self.env.user.company_id.pabietax_password
        # connect with server
        uid = self._connect_docsign_server(url, db, username, password)

        active_ids = self._context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(active_ids)
        # call method in server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))
        voucher_dict = self._prepare_voucher(voucher_ids)
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'generate_pdf_file_link', [voucher_dict])

        self.with_context(
            {'preview': True})._create_attachment(res_ids)
        return True
