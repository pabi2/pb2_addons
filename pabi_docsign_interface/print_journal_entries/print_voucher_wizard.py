# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xmlrpclib
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

CANCELLATION = ('customer_cancel')

class PrintVoucherWizard(models.TransientModel):
    _inherit = 'print.voucher.wizard'

    state_sign = fields.Selection([
        ('waiting', 'Waiting'),
        ('signed', 'Signed'), ],
        string="State Sign",
        default=lambda self: self._get_default_state(),
        readonly=True,
    )

    reason_text = fields.Text()

    @api.multi
    def _get_default_state(self):
        active_ids = self._context.get('active_ids')
        account_ids = self.env['account.move'].browse(active_ids)
        state = account_ids.mapped('state_sign')
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
    def _check_origin_payment(self, voucher):
        self.ensure_one()
        Voucher = self.env['account.voucher']
        origin = Voucher.search([('number', '=', voucher), ('state', '=', 'cancel'), ('state_sign', '=', 'signed')])
        return origin.number_preprint

    @api.multi
    def _get_taxbranch_id(self, voucher):
        Voucher = self.env['account.voucher']
        origin = Voucher.search([('number', '=', voucher), ('state', '=', 'cancel'), ('state_sign', '=', 'signed')])
        taxbranch_id = origin.line_ids[0].invoice_id.taxbranch_id
        return taxbranch_id

    @api.multi
    def _get_line_ids(self, voucher):
        Voucher = self.env['account.voucher']
        origin = Voucher.search([('number', '=', voucher), ('state', '=', 'cancel'), ('state_sign', '=', 'signed')])
        line_ids = origin.line_ids
        return line_ids

    @api.multi
    def _get_line_ids(self, voucher):
        Voucher = self.env['account.voucher']
        origin = Voucher.search([('number', '=', voucher), ('state', '=', 'cancel'), ('state_sign', '=', 'signed')])
        line_ids = origin.line_ids
        return line_ids

    @api.multi
    def _prepare_voucher(self, account_ids):
        self.ensure_one()
        account_dict = []
        reason = ""
        reason_text = ""
        active_id = self._context.get('active_id', False)
        move_id = self.env['account.move'].browse(active_id)
        origin_preprint = self._check_origin_payment(move_id.document)
        seller = self.env.user.company_id.partner_id
        for voucher in account_ids:
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
            taxbranch_id = self._get_taxbranch_id(move_id.document)
            line_ids = []
            for voucher_line in self._get_line_ids(move_id.document):
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
            account_dict.append({
                # header
                'doctype': 'T07',
                'docform' : 'customer_cancel',
                # 'lang_form': 'Tha',
                'number': voucher.name,
                'customer_code': voucher.partner_id.search_key,
                'customer_name': voucher.partner_id.name,
                'seller_name': seller.name,
                'currency': "THB",
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
                'system_origin_name': 'pabi2',
                'system_origin_number': voucher.ref,
                'origin_id': origin_preprint,
                'user_sign': self.env.user.name,
                'approved_by': self.env.user.name,  # TODO: Waiting new pg.
                'rdx_no': '',  # TODO: Waiting RDX
                # lines
                'printing_lines': line_ids,
            })
        return account_dict

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
        return account_dict

    @api.multi
    def _create_attachment(self, res_ids):
        self.ensure_one()
        account_obj = self.env['account.move']
        attachment_obj = self.env['ir.attachment']
        account_ids = self.env['account.move']
        for res in res_ids:
            if res['status'] == 'OK':
                preview = self._context.get('preview')
                account_id = account_obj.search([('number', '=', res['name'])])
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
                    'res_model': account_id._name,
                    'res_id': account_id.id,
                })
                account_id.write({
                    'number_preprint_current': res['preprint_number']
                })
                account_ids |= account_id
            else:
                raise ValidationError(_("%s" % res['errorMessage']))
        return account_ids

    @api.multi
    def _stamp_voucher_pdf(self, account_dict, models, db, uid, password):
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'action_call_service', [account_dict])
        voucher_ok = self._create_attachment(res_ids)
        voucher_ok.write({'state_sign': 'signed'})
        return True

    @api.multi
    def action_sign_voucher(self):
        company_id = self.env.user.company_id
        url = company_id.pabietax_web_url_test or company_id.pabietax_web_url
        db = company_id.pabietax_db
        username = company_id.pabietax_user
        password = company_id.pabietax_password
        edit_sign = self._context.get("Edit_sign", False)
        # connect with server
        uid = self._connect_docsign_server(url, db, username, password)

        active_ids = self._context.get('active_ids')
        account_ids = self.env['account.move'].browse(active_ids)
        # call method in server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))
        account_dict = self._prepare_voucher(account_ids)
        if edit_sign:
            self._check_edit_value(account_dict, models, db, uid, password)
        self._stamp_voucher_pdf(account_dict, models, db, uid, password)
        return True

    @api.multi
    def action_preview_voucher(self):
        company_id = self.env.user.company_id
        url = company_id.pabietax_web_url_test or company_id.pabietax_web_url
        db = company_id.pabietax_db
        username = company_id.pabietax_user
        password = company_id.pabietax_password
        # connect with server
        uid = self._connect_docsign_server(url, db, username, password)

        active_ids = self._context.get('active_ids')
        account_ids = self.env['account.move'].browse(active_ids)
        # call method in server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))
        account_dict = self._prepare_voucher(account_ids)
        res_ids = models.execute_kw(
            db, uid, password, 'account.printing',
            'generate_pdf_file_link', [account_dict])
        self.with_context(
            {'preview': True})._create_attachment(res_ids)
        return True
