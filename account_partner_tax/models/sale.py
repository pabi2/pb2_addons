# -*- coding: utf-8 -*-
from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change(self, pricelist, product, qty=0, uom=False,
                          qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False, fiscal_position=False, flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            tax_ids = partner.customer_tax_ids.ids
            if tax_ids:
                tax_ids = list(set(res['value'].get('tax_id', []) + tax_ids))
                res['value']['tax_id'] = tax_ids
        return res
