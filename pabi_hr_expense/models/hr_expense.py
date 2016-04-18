# -*- coding: utf-8 -*-

from openerp import models, fields


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    apweb_ref_url = fields.Char(
        string='AP-Web Ref.',
    )
    is_employee_advance = fields.Boolean(
        string='Employee Advance',
        default=lambda self: self._context.get('is_employee_advance', False),
    )
    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Clearing for Advance',
    )
    employee_bank_id = fields.Many2one(
        'res.bank.master',
        string='Bank',
    )


class HRExpenseRule(models.Model):
    _name = "hr.expense.rule"

    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        required=True,
    )
    position = fields.Char(
        string='Position',
    )
    condition_1 = fields.Char(
        string='Condition 1',
    )
    condition_2 = fields.Char(
        string='Condition 2',
    )
    uom = fields.Char(
        string='UoM',
    )
    amount = fields.Float(
        string='Amount',
        default=0.0,
        required=True,
    )
    _sql_constraints = [
        ('rule_unique',
         'unique(activity_id, position, condition_1, condition_2, uom)',
         'Expense Regulation must be unique!'),
    ]
