# -*- coding: utf-8 -*-
from openerp import api, models
from .account_activity import ActivityCommon


class HRSalaryeExpense(models.Model):
    _inherit = 'hr.salary.expense'

    @api.multi
    def action_submit(self):
        for request in self:
            for line in request.line_ids:
                Analytic = self.env['account.analytic.account']
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
        return super(HRSalaryeExpense, self).action_submit()


class HRSalaryLine(ActivityCommon, models.Model):
    _inherit = 'hr.salary.line'
