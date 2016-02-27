# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    product_name = fields.Char(string='Description')

    @api.model
    def open_price_comparison(self, ids):
        window_obj = self.env["ir.actions.act_window"]
        res = window_obj.for_xml_id('purchase', 'purchase_line_form_action2')
        pur_line_ids = []
        po_recs = self.browse(ids)
        for po_rec in po_recs:
            pur_line_ids = po_rec.purchase_ids._ids
        res['context'] = self._context
        res['domain'] = [('order_id', 'in', pur_line_ids)]
        return res


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    product_name = fields.Char(string='Description')

    @api.multi
    def onchange_product_id(self, product_id, product_uom_id,
                            parent_analytic_account, analytic_account,
                            parent_date, date):
        res = super(PurchaseRequisitionLine, self).\
            onchange_product_id(product_id, product_uom_id,
                                parent_analytic_account, analytic_account,
                                parent_date, date)
        if 'value' in res:
            if 'product_qty' in res['value']:
                del res['value']['product_qty']
        return res
