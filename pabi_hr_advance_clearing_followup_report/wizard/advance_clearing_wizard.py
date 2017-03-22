# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta

from openerp import models, api, fields


class AdvanceClearingFollowupWizard(models.Model):
    _name = "advance.clearing.followup.wizard"

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
    )
    date_from = fields.Date(
        string="Date From",
        required=True,
        default=lambda *a: time.strftime('%Y-%m-01'),
    )
    date_to = fields.Date(
        string="Date To",
        required=True,
        default=lambda *a: str(
            datetime.now() + relativedelta.relativedelta(
                months=+1, day=1, days=-1))[:10],
    )
    expense_ids = fields.Many2many(
        'hr.expense.expense',
        string="Advance Number",
        required=True,
    )

    @api.multi
    def run_report(self):
        self.ensure_one()
        expenses = self.expense_ids.ids
        action = self.env.ref(
            'pabi_hr_advance_clearing_followup_report.action_advance_clearing_followup'
        )
        action_data = action.read()[0]
        domain = [
            ('advance_expense_id', 'in', expenses),
            ('employee_id', '=', self.employee_id.id),
        ]
        action_data['domain'] = domain
        return action_data
