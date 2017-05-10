# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class BudgetTransition(models.Model):
    _name = 'budget.transition'
    _description = 'Keep tranck of budget transition from one model to another'

    expense_line_id = fields.Many2one(
        'hr.expense.line',
        string='Expense Line',
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
    )
    invoice_state = fields.Char(
        string='Invoice State',
    )
    quantity = fields.Float(
        string='Quantity',
    )
    forward = fields.Boolean(
        string='Forward',
        default=False,
        help="True, when the end document trigger budget transition",
    )
    backward = fields.Boolean(
        string='Backward',
        default=False,
        help="True, when the end document that forwarded, has been cancelled",
    )


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _create_supplier_invoice_from_expense(self, merge_line=False):
        invoice = super(HRExpenseExpense, self).\
            _create_supplier_invoice_from_expense(merge_line=merge_line)
        expense = self
        # As invoice is created, log into budget.transition
        


        return invoice
