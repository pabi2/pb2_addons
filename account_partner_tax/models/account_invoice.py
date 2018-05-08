# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          currency_id=False, company_id=None):
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            tax_ids = []
            if type in ('out_invoice', 'out_refund'):
                tax_ids = partner.customer_tax_ids.ids
            elif type in ('in_invoice', 'in_refund'):
                tax_ids = partner.supplier_tax_ids.ids
            if tax_ids:
                tax_ids = list(set(
                    res['value'].get('invoice_line_tax_id', []) + tax_ids))
                res['value']['invoice_line_tax_id'] = tax_ids
        return res
