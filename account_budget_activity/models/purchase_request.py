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
        required=True,
        compute='_compute_activity_group',
        store=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=False,
    )

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
