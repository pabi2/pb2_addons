# -*- coding: utf-8 -*-
from openerp import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def onchange_product_id(self, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft'):

        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            tax_ids = partner.supplier_tax_ids.ids
            if tax_ids:
                tax_ids = list(set(res['value'].get('taxes_id', []) + tax_ids))
                res['value']['taxes_id'] = tax_ids
        return res
