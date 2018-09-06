# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp.api import Environment
from openerp.exceptions import ValidationError


class AccountFiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    def init(self, cr):
        env = Environment(cr, SUPERUSER_ID, {})
        fiscalyears = env['account.fiscalyear'].search([])
        fiscalyears.create_budget_level_config()


class AccountFiscalyearBudgetLevel(models.Model):
    _inherit = 'account.fiscalyear.budget.level'
    _rec_name = 'budget_level'

    budget_release = fields.Selection(
        selection_add=[('auto_rolling', 'Auto Release as Rolling'), ],
        help="* Budget Line: to release budget at budget line\n"
        "* Budget Header: to release budget at budget header, "
        "it will then release that full amount in 1st budget line\n"
        "* Auto Release as Planned: always set released "
        "amount equal to plan amount\n"
        "* Auto Release as Rolling: always set released "
        "amount equal to each line rolling amount"
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        """
        For invoice, analytic line will be created before post, so we want to
            check for budget before post, to minimize lock of sequence number
        For non-invoice (JE), we do it after posted.
        """
        if self._context.get('invoice', False):
            self._move_budget_check()
        res = super(AccountMove, self).post()
        if not self._context.get('invoice', False):
            self._move_budget_check()
        return res

    @api.multi
    def _move_budget_check(self):
        Budget = self.env['account.budget']
        AnalyticLine = self.env['account.analytic.line']
        for move in self:
            analytic_lines = AnalyticLine.search([
                ('move_id', 'in', move.line_id._ids)
            ])
            if not analytic_lines:
                continue
            doc_date = move.date
            doc_lines = Budget.convert_lines_to_doc_lines(analytic_lines)
            res = Budget.post_commit_budget_check(doc_date, doc_lines)
            if not res['budget_ok']:
                raise ValidationError(res['message'])
        return True
