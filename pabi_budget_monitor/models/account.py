# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp import SUPERUSER_ID
from openerp.api import Environment
from openerp.exceptions import Warning as UserError


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    def init(self, cr):
        env = Environment(cr, SUPERUSER_ID, {})
        fiscalyears = env['account.fiscalyear'].search([])
        fiscalyears.create_budget_level_config()


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        res = super(AccountMove, self).post()
        self._move_budget_check()
        return res

    @api.multi
    def _move_budget_check(self):
        Budget = self.env['account.budget']
        AnalyticLine = self.env['account.analytic.line']
        for move in self:
            if move.state == 'posted':
                analytic_lines = AnalyticLine.search([
                    ('move_id', 'in', move.line_id._ids)
                ])
                if not analytic_lines:
                    continue
                doc_date = move.date
                doc_lines = Budget.convert_lines_to_doc_lines(analytic_lines)
                res = Budget.post_commit_budget_check(doc_date, doc_lines)
                if not res['budget_ok']:
                    raise UserError(res['message'])
        return True
