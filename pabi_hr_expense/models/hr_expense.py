# -*- coding: utf-8 -*-

from openerp import models, fields, api


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    apweb_ref_url = fields.Char(
        string='AP-Web Ref.',
    )
    create_uid = fields.Many2one(
        'res.users',
        string='Created By',
        readonly=True,
    )
    date_back = fields.Date(
        string='Back from seminar',
    )
    date_due = fields.Date(
        string='Due Date',
        related='advance_due_history_ids.date_due',
        store=True,
    )
    employee_bank_id = fields.Many2one(
        'res.bank.master',
        string='Bank',
    )
    outstanding_advance_count = fields.Integer(
        string='Outstanding Advance Count',
        compute='_compute_outstanding_advance_count',
    )
    state = fields.Selection(
        [('draft', 'Wait for Accept'),
         ('cancelled', 'Refused'),
         ('confirm', 'Accepted'),
         ('accepted', 'Approved'),
         ('done', 'Waiting Payment'),
         ('paid', 'Paid'),
         ]
    )
    advance_type = fields.Selection(
        [('buy_product', 'Buy Product/Material'),
         ('attend_seminar', 'Attend Seminar'),
         ]
    )
    advance_due_history_ids = fields.One2many(
        'hr.expense.advance.due.history',
        'expense_id',
        string='Due History',
        readonly=True,
    )

    @api.model
    def _get_outstanding_advance_domain(self):
        domain = [('employee_id', '=', self.employee_id.id),
                  ('is_employee_advance', '=', True)]
        return domain

    @api.multi
    def _compute_outstanding_advance_count(self):
        for rec in self:
            domain = rec._get_outstanding_advance_domain()
            self.outstanding_advance_count = self.search_count(domain)

    @api.multi
    def action_open_outstanding_advance(self):
        self.ensure_one()
        action = self.env.ref('hr_expense_advance_clearing.'
                              'action_expense_advance')
        result = action.read()[0]
        # Find outstanding
        domain = self._get_outstanding_advance_domain()
        result.update({'domain': domain})
        return result


class HRExpenseAdvanceDueHistory(models.Model):
    _name = 'hr.expense.advance.due.history'
    _order = 'write_date desc'

    expense_id = fields.Many2one(
        'hr.expense',
        string='Expense',
        ondelete='cascade',
        index=True,
    )
    date_due = fields.Date(
        string='New Due Date',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Updated By',
        readonly=True,
    )
    write_date = fields.Datetime(
        string='Updated Date',
        readonly=True,
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
