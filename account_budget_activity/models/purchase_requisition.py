# -*- coding: utf-8 -*-
from openerp import api, fields, models


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


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        compute='_compute_activity_group',
        store=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    purchase_line_ids = fields.One2many(
        'purchase.order.line',
        'requisition_line_id',
        string='Purchase Order Lines',
        readonly=True,
    )

    @api.one
    @api.depends('product_id', 'activity_id')
    def _compute_activity_group(self):
        if self.product_id and self.activity_id:
            self.product_id = self.activity_id = False
        if self.product_id:
            account_id = self.product_id.property_account_expense.id or \
                self.product_id.categ_id.property_account_expense_categ.id
            activity_group = self.env['account.activity.group'].\
                search([('account_id', '=', account_id)])
            self.activity_group_id = activity_group
        elif self.activity_id:
            self.activity_group_id = self.activity_id.activity_group_id
