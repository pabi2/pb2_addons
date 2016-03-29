# -*- coding: utf-8 -*-
# © 2015 TrinityRoots
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_purchase_requisition_line(pr, item)
        if 'price_unit' not in res:
            res.update({'price_unit': item.price_unit})
        if 'taxes_id' not in res:
            res.update(
                {
                    'taxes_id': [(4,item.line_id.taxes_id.ids)],
                }
            )
        return res

    @api.model
    def _prepare_purchase_requisition(self, picking_type_id, company_id):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_purchase_requisition(picking_type_id, company_id)
        pr_line_obj = self.env['purchase.request.line']
        active_id = self._context['active_ids'][0]
        req_id = pr_line_obj.browse(active_id).request_id
        vals = {
            'user_id': req_id.responsible_person.id,
            'description': req_id.description,
            'objective': req_id.objective,
            'currency_id': req_id.currency_id.id,
            'purchase_type_id': req_id.purchase_type_id.id,
            'purchase_method_id': req_id.purchase_method_id.id,
            'total_budget_value': req_id.total_budget_value,
            'prototype': req_id.prototype,
        }
        res.update(vals)
        return res

    @api.model
    def _prepare_item(self, line):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self)\
            ._prepare_item(line)
        if 'price_unit' not in res:
            res.update({'price_unit': line.price_unit})
        if 'taxes_id' not in res:
            res.update({'taxes_id': line.taxes_id.ids})
        return res


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"

    price_unit = fields.Float(
        'Unit Price',
        track_visibility='onchange',
    )
    taxes_id = fields.Many2many(
        'account.tax',
        'purchase_request_make_requisition_taxes_rel',
        'item_id',
        'tax_id',
        string='Taxes'
    )
