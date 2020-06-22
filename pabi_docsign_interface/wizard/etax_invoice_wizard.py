# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import xmlrpclib
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class eTaxInvoiceWizard(models.TransientModel):
    _name = 'etax.invoice'
    _description = 'call server eTax printting'

    form_name = fields.Selection(
        [('80', 'Debit note'),
         ('81', 'Credit note'),
         ('380', 'Invoice'),
         ('388', 'Tax Invoice'),
         ('T01', 'Receipt'),
         ('T02', 'Invoice/ Tax Invoice'),
         ('T03', 'Receipt/ Tax Invoice'),
         ('T04', 'Delivery order / TaxInvoice'),
         ('T05', 'Abbreviated Tax Invoice'),
         ('T06', 'Receipt /Abbreviated Tax Invoice'),
         ('T07', 'Cancellation note')],
        string="Form",
        required=True,
    )

    @api.multi
    def _connect_docsign_server(self, url, db, username, password):
        self.ensure_one()
        # connect with docsign server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/common'.format(url))
        uid = models.authenticate(db, username, password, {})
        return uid

    @api.multi
    def _prepare_invoice(self, invoice_ids):
        self.ensure_one()
        invoice_dict = []
        # seller by company
        seller = self.env.user.company_id.partner_id
        for inv in invoice_ids:
            # invoice lines
            line_ids = [(0, 0, {
                'name': line.name,
                'quantity': line.quantity,
                # 'uom': line,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                # 'product_id': 1,  # TODO: used name instead
                # 'product_uom_id': 18,  # TODO: used name instead
                # 'taxes': line,
                }) for line in inv.invoice_line]

            # create invoice printing document
            invoice_dict.append({
                # header
                'number': inv.number,
                'customer_name': inv.partner_id.name,
                'seller_name': seller.name,
                'currency': inv.currency_id.name,
                'invoice_date': inv.date_invoice,  # document create date
                'operating_unit': inv.operating_unit_id.name,
                'notes': inv.comment,
                # customer information
                'customer_street': inv.partner_id.street,
                'customer_street2': inv.partner_id.street2,
                # 'customer_city': '',
                # 'customer_state': '',
                'customer_zip': inv.partner_id.zip,
                'customer_country_code':
                    inv.partner_id.country_id.code or 'TH',
                'customer_vat': inv.partner_id.vat,
                'customer_phone':
                    inv.partner_id.phone or inv.partner_id.mobile,
                'customer_email': inv.partner_id.email,
                # seller information
                'seller_street': seller.street,
                'seller_street2': seller.street2,
                # 'seller_city': '',
                # 'seller_state': '',
                'seller_zip': seller.zip,
                'seller_country_code': seller.country_id.code or 'TH',
                'seller_vat': seller.vat,
                'seller_phone': seller.phone or seller.mobile,
                'seller_email': seller.email,
                'amount_untaxed': inv.amount_untaxed,
                'amount_tax': inv.amount_tax,
                'amount_total': inv.amount_total,
                # tax branch information
                'taxbranch_name': inv.taxbranch_id.name,
                'taxbranch_code': inv.taxbranch_id.code,
                'taxbranch_taxid': inv.taxbranch_id.taxid,
                # lines
                'printing_lines': line_ids,
                # 'name': '%s/%s' % (inv.number, randint(0, 999999)),  # Test
            })
        return invoice_dict

    @api.multi
    def _stamp_invoice_pdf(self, ids, invoice_ids, models, db, uid, password):
        inv_obj = self.env['account.invoice']
        attachment_obj = self.env['ir.attachment']
        res_ids = models.execute_kw(
            db, uid, password, 'account.invoice.printing',
            'action_call_service', [ids])

        for res in res_ids:
            if res['status'] == 'OK':
                inv_id = inv_obj.search([('number', '=', res['name'])])
                # create url attachment
                attachment_obj.create({
                    'name': _("%s.pdf") % res['name'],
                    'type': 'url',
                    'url': res['link_download'],
                    'res_model': invoice_ids._name,
                    'res_id': inv_id.id,
                })
                inv_id.write({'state_sign': 'signed'})
        return True

    @api.multi
    def print_etax(self):
        url = self.env.user.company_id.pabietax_web_url
        db = self.env.user.company_id.pabietax_db
        username = self.env.user.company_id.pabietax_user
        password = self.env.user.company_id.pabietax_password
        # connect with server
        uid = self._connect_docsign_server(url, db, username, password)
        if not uid:
            raise ValidationError(_('Connected with server error.'))

        active_ids = self._context.get('active_ids')
        invoice_ids = self.env['account.invoice'].browse(active_ids)
        # call method in server
        models = xmlrpclib.ServerProxy('{}/xmlrpc/object'.format(url))
        invoice_dict = self._prepare_invoice(invoice_ids)
        # create (multi) invoice in server
        inv_server = models.execute_kw(
            db, uid, password, 'account.invoice.printing',
            'create', [invoice_dict])
        # call method to stamp pdf
        self._stamp_invoice_pdf(inv_server, invoice_ids,
                                models, db, uid, password)
        return True
