# -*- coding: utf-8 -*-
from openerp import api, fields, models


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def expense_accept(self):
        for expense in self:
            for line in expense.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account = \
                    Analytic.create_matched_analytic(line)
        return super(HRExpenseExpense, self).expense_accept()

    @api.model
    def _prepare_inv_line(self, account_id, exp_line):
        res = super(HRExpenseExpense, self)._prepare_inv_line(account_id,
                                                              exp_line)
        AnayticAccount = self.env['account.analytic.account']
        dimensions = AnayticAccount._analytic_dimensions()
        for d in dimensions:
            res.update({d: exp_line[d].id})
        return res


class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

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

