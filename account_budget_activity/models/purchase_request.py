# -*- coding: utf-8 -*-
from openerp import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.multi
    def button_to_approve(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(PurchaseRequest, self).button_to_approve()


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

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
    purchased_qty = fields.Float(
        string='Purchased Quantity',
        digits=(12, 6),
        compute='_compute_purchased_qty',
        store=True,
        help="This field calculate purchased quantity at line level. "
        "Will be used to calculate committed budget",
    )

    @api.multi
    @api.depends('requisition_lines.purchase_line_ids.order_id.state')
    def _compute_purchased_qty(self):
        Uom = self.env['product.uom']
        for request_line in self:
            purchased_qty = 0.0
            for reqisition_line in request_line.requisition_lines:
                for purchase_line in reqisition_line.purchase_line_ids:
                    if purchase_line.order_id.state in ['approved']:
                        # Purchased Qty in PO Line's UOM
                        purchased_qty += \
                            Uom._compute_qty(purchase_line.product_uom.id,
                                             purchase_line.product_qty,
                                             request_line.product_uom_id.id)
            request_line.purchased_qty = min(request_line.product_qty,
                                             purchased_qty)

    @api.one
    @api.depends('product_id', 'activity_id')
    def _compute_activity_group(self):
        if self.product_id and self.activity_id:
            self.product_id = self.activity_id = False
            self.name = False
        if self.product_id:
            account_id = self.product_id.property_account_expense.id or \
                self.product_id.categ_id.property_account_expense_categ.id
            activity_group = self.env['account.activity.group'].\
                search([('account_id', '=', account_id)])
            self.activity_group_id = activity_group
        elif self.activity_id:
            self.activity_group_id = self.activity_id.activity_group_id
            self.name = self.activity_id.name
