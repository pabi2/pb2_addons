# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountBudgetInitLine(models.Model):
    _name = "account.budget.init.line"
    _description = "Init Expense line"

    budget_id = fields.Many2one(
        comodel_name='account.budget',
        string='Budget',
        ondelete='cascade',
        index=True,
        required=True,
    )
    budgeted_expense_external = fields.Float()
    budgeted_expense_internal = fields.Float()
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    income_section_id = fields.Many2one(
        comodel_name='res.section',
        string='Income Section',
    )
    fund_id = fields.Many2one(
        comodel_name='res.fund',
        string='Fund',
    )
    cost_control_id = fields.Many2one(
        comodel_name='cost.control',
        string='Job Order',
    )
    activity_group_id = fields.Many2one(
        comodel_name='account.activity.group',
        string='Activity Group',
    )
    description = fields.Char(
        string='Description',
        size=500,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )
    released_amount = fields.Float(
        string='Released Amount',
    )
    m1 = fields.Float(
        string='Oct',
    )
    m2 = fields.Float(
        string='Nov',
    )
    m3 = fields.Float(
        string='Dec',
    )
    m4 = fields.Float(
        string='Jan',
    )
    m5 = fields.Float(
        string='Feb',
    )
    m6 = fields.Float(
        string='Mar',
    )
    m7 = fields.Float(
        string='Apr',
    )
    m8 = fields.Float(
        string='May',
    )
    m9 = fields.Float(
        string='Jun',
    )
    m10 = fields.Float(
        string='Jul',
    )
    m11 = fields.Float(
        string='Aug',
    )
    m12 = fields.Float(
        string='Sep',
    )
