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

    state_sign = fields.Char(
        default=lambda self: self._get_default_state('state_sign'),
        readonly=True,
    )
    state = fields.Char(
        default=lambda self: self._get_default_state('state'),
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
    reason_dcn_code = fields.Selection([
        ('CDNG01', 'ลดราคาสินค้าที่ขาย (สินค้าผิดข้อกำหนดที่ตกลงกัน)'),
        ('CDNG02', 'สินค้าชำรุดเสียหาย'),
        ('CDNG03', 'สินค้าขาดจำนวนตามที่ตกลงซื้อขาย'),
        ('CDNG04', 'คำนวณราคาสินค้าผิดพลาดสูงกว่าที่เป็นจริง'),
        ('CDNG05', 'รับคืนสินค้า (ไม่ตรงตามคำพรรณนา)'),
        ('CDNG99', 'เหตุอื่น (ระบุสาเหตุ)')],
        string="Reason for cancellation",
    )
    reason_text = fields.Text()

    @api.multi
    def _get_default_state(self, state):
        active_ids = self._context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(active_ids)
        state = voucher_ids.mapped(state)
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
    def _prepare_voucher(self, voucher_ids):
        self.ensure_one()
        voucher_dict = []
        reason = ""
        reason_text = ""
        doctype = ""
        cancel_form = self._context.get("cancel_sign", False)
        if voucher_ids.filtered(lambda l: l.doc_print and l.doc_print != self.doc_print):
            raise ValidationError(_("Report Type is not equal document sign."))
        if cancel_form and voucher_ids.filtered(lambda l: l.state != 'cancel'):
            raise ValidationError(_("State document is not cancel."))
        if self.doc_print in TAX_RECEIPT:
            if cancel_form:
                if not self.reason_dcn_code:
                    raise ValidationError(_(
                        "This Form can't cancel sign. "
                        "you have to choose Reason for cancellation."
                    ))
                doctype = '81'
                reason = self.reason_dcn_code
            else:
                doctype = 'T03'
                reason = self.reason_tax_receipt_update
            if self.reason_tax_receipt_update == 'TIVC99' or self.reason_dcn_code == 'CDNG99':
                reason_text = self.reason_text
        elif self.doc_print in RECEIPT:
            doctype = cancel_form and 'T07' or 'T01'
            reason = self.reason_receipt_update
            if self.reason_receipt_update == 'RCTC99':
                reason_text = self.reason_text
        else:
            raise ValidationError(_("This Form can't sign."))
        # seller by company
        seller = self.env.user.company_id.partner_id
        for voucher in voucher_ids:
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
            origin = cancel_form and voucher.number_preprint_current or False
            # invoice lines
            line_ids = []
            taxbranch_id = voucher.line_ids[0].invoice_id.taxbranch_id
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
                'number': voucher.number_preprint or voucher.id,
                'cancel_form': cancel_form,
                'customer_code': voucher.partner_id.search_key,
                'customer_name': voucher.partner_id.name,
                'seller_name': seller.name,
                'currency': voucher.currency_id.name,
                'date_document': voucher.date,
                'create_document': voucher.date_document,
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
                'customer_province_code':
                    voucher.partner_id.province_id.code,
                'customer_district_code':
                    voucher.partner_id.district_id.code,
                'customer_subdistrict_code':
                    voucher.partner_id.township_id.code,
                'customer_vat': voucher.partner_id.vat,
                'customer_phone':
                    voucher.partner_id.phone or voucher.partner_id.mobile,
                'customer_email': voucher.partner_id.email,
                'customer_taxbranch_code': voucher.partner_id.taxbranch,
                'customer_taxbranch_name': 'สำนักงานใหญ่',
                'customer_is_company': voucher.partner_id.is_company,
                # seller information
                'seller_street': seller.street,
                'seller_street2': seller.street2,
                'seller_city': '',
                'seller_state': '',
                'seller_zip': seller.zip,
                'seller_country_code': seller.country_id.code or 'TH',
                'seller_province_code':
                    seller.province_id.code,
                'seller_district_code':
                    seller.district_id.code,
                'seller_subdistrict_code':
                    seller.township_id.code,
                'seller_building_number': seller.street.split(' ')[0],
                'seller_vat': taxbranch_id.taxid,
                'seller_phone': taxbranch_id.phone,
                'seller_fax': taxbranch_id.fax,
                'seller_email': seller.email,
                'seller_taxbranch_code': taxbranch_id.code or '00000',
                'seller_taxbranch_name': taxbranch_id.name or '',
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
                # origin
                'origin_id': origin,
                'system_origin_name': 'pabi2',
                'system_origin_number': cancel_form and voucher.cancel_move_id.name or voucher.number or voucher.id,
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
        move_obj = self.env['account.move']
        attachment_obj = self.env['ir.attachment']
        voucher_ids = self.env['account.voucher']
        cancel_form = self._context.get("cancel_sign", False)
        for res in res_ids:
            if res['status'] == 'OK':
                preview = self._context.get('preview')
                state_draft = self._context.get('draft')
                domain = [('number', '=', res['name'])]
                if cancel_form:
                    move_id = move_obj.search([('name', '=', res['name'])])
                    domain = [('number', '=', move_id.ref)]
                elif state_draft:
                    domain = [('id', '=', res['name'])]
                voucher_id = voucher_obj.search(domain)
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
        cancel_form = self._context.get("cancel_sign", False)
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'action_call_service', [voucher_dict])
        voucher_ok = self._create_attachment(res_ids)
        state = 'signed'
        if cancel_form:
            state = 'cancel'
        voucher_ok.write({'state_sign': state, 'doc_print': self.doc_print})
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
        edit_sign = self._context.get("edit_sign", False)
        # connect with server
        db, password, uid, models = self._connect_docsign_server()
        # Prepare Value
        active_ids = self._context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(active_ids)
        if voucher_ids.filtered(lambda l: l.state == 'draft'):
            raise ValidationError(_("State draft can not sign."))
        voucher_dict = self._prepare_voucher(voucher_ids)
        # call method in server
        if edit_sign:
            self._check_edit_value(voucher_dict, models, db, uid, password)
        self._stamp_voucher_pdf(voucher_dict, models, db, uid, password)
        return True

    @api.multi
    def action_preview_account_voucher(self):
        ctx = self._context.copy()
        # connect with server
        db, password, uid, models = self._connect_docsign_server()
        # Prepare Value
        active_ids = self._context.get('active_ids')
        voucher_ids = self.env['account.voucher'].browse(active_ids)
        ctx.update({'preview': True})
        if voucher_ids.filtered(lambda l: l.state == 'draft'):
            ctx.update({'draft': True})
        voucher_dict = self._prepare_voucher(voucher_ids)
        # call method in server
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'generate_pdf_file_link', [voucher_dict])

        self.with_context(ctx)._create_attachment(res_ids)
        return True
