# -*- coding: utf-8 -*-

from openerp import models, fields, api


class DateValueHistory(models.Model):
    _name = 'date.value.history'

    name = fields.Char(
        compute='_compute_name',
        string='Name',
        store=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Supplier Payment',
        required=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Supplier Invoice',
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
    )
    date_value = fields.Date(
        string='Value Date',
    )
    amount = fields.Float(
        string='Amount',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
    )
    date = fields.Date(
        string='Created On',
    )
    reason = fields.Char(
        string="Reason",
    )

    @api.depends('voucher_id', 'voucher_id.number',
                 'invoice_id', 'invoice_id.number',
                 'expense_id', 'expense_id.number')
    def _compute_name(self):
        for record in self:
            record.name = '%s-%s-%s' % (record.voucher_id.number or '_',
                                        record.invoice_id.number or '_',
                                        record.expense_id.number or '_')


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    date_value_history_ids = fields.One2many(
        'date.value.history',
        'expense_id',
        string='Value Date History',
        readonly=True,
    )
