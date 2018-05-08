# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .account_activity import ActivityCommon


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def tender_in_progress(self):
        for requisition in self:
            for line in requisition.line_ids:
                Analytic = self.env['account.analytic.account']
                line.account_analytic_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequisition, self).tender_in_progress()

    @api.model
    def _prepare_purchase_order_line(self, requisition, requisition_line,
                                     purchase_id, supplier):
        res = super(PurchaseRequisition, self).\
            _prepare_purchase_order_line(requisition, requisition_line,
                                         purchase_id, supplier)
        res.update({
            'requisition_line_id': requisition_line.id,
        })
        # Dimension
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: requisition_line[d].id})
        return res


class PurchaseRequisitionLine(ActivityCommon, models.Model):
    _inherit = 'purchase.requisition.line'

    purchase_line_ids = fields.One2many(
        'purchase.order.line',
        'requisition_line_id',
        string='Purchase Order Lines',
        readonly=True,
    )
