# -*- coding: utf-8 -*-

from openerp import api, models, fields


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition"

    @api.model
    def _prepare_item(self, line):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_item(line)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: line[d].id})
        return res

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        res = super(PurchaseRequestLineMakePurchaseRequisition, self).\
            _prepare_purchase_requisition_line(pr, item)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: item[d].id})
        return res


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.requisition.item"

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=False,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=False,
    )
