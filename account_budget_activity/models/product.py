# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    income_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Income Activity Group',
        compute='_compute_activity_group_id',
    )
    expense_activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Expense Activity Group',
        compute='_compute_activity_group_id',
    )

    @api.multi
    @api.depends('property_account_expense_categ',
                 'property_account_income_categ')
    def _compute_activity_group_id(self):
        for rec in self:
            if rec.property_account_expense_categ:
                activity_group = self.env['account.activity.group'].\
                    search([('account_id', '=',
                             rec.property_account_expense_categ.id)])
                rec.expense_activity_group_id = activity_group
            if rec.property_account_income_categ:
                activity_group = self.env['account.activity.group'].\
                    search([('account_id', '=',
                             rec.property_account_income_categ.id)])
                rec.income_activity_group_id = activity_group
