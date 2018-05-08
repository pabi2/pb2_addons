# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AdvanceClearingFollowupWizard(models.TransientModel):
    _name = "advance.clearing.followup.wizard"

    run_date = fields.Date(
        string='Run Date',
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
    )
    show_open_item_only = fields.Boolean(
        string='Show open item only',
        default=True,
    )
    specific_employee = fields.Boolean(
        string='Specify Employee(s)',
        default=False,
        help="If unchecked, show all advance for all employees",
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees",
        required=False,
    )

    @api.multi
    def run_report(self):
        self.ensure_one()
        action = self.env.ref(
            'pabi_hr_advance_clearing_followup_report.'
            'action_advance_clearing_followup'
        )
        action_data = action.read()[0]
        domain = [('is_employee_advance', '=', True), ('state', '=', 'paid')]
        if self.show_open_item_only:
            domain.append(('amount_to_clearing', '>', 0.0))
        if self.specific_employee:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        expense_ids = self.env['hr.expense.expense'].search(domain).ids
        action_data['domain'] = [('advance_expense_id', 'in', expense_ids)]
        return action_data
