# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class BudgetReleaseWizard(models.TransientModel):
    _name = "budget.release.wizard"

    progress = fields.Float(
        string='Progress',
        readonly=True,
    )
    amount_to_release = fields.Float(
        string="Amount To Release",
    )

    @api.onchange('amount_to_release')
    def _onchange_amount_to_release(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        BudgetLine = self.env['account.budget.line']
        budget_lines = False
        if active_model == 'account.budget.line':
            budget_lines = BudgetLine.search([('id', '=', active_id)])
        elif active_model == 'account.budget':
            budget_lines = BudgetLine.search([('budget_id', '=', active_id)])

        planned_amount = sum([l.planned_amount for l in budget_lines])
        if not planned_amount:
            self.progress = 0.0
        else:
            self.progress = self.amount_to_release / planned_amount * 100

    @api.model
    def default_get(self, fields):
        res = super(BudgetReleaseWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        budget_line = self.env['account.budget.line'].browse(active_id)
        budget_release = budget_line.budget_id.budget_level_id.budget_release
        if budget_release != 'manual_line':
            raise ValidationError(_('Manual budget released not allowed!'))
        res['amount_to_release'] = budget_line.released_amount
        return res

    @api.multi
    def do_release(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        budget_line = self.env['account.budget.line'].browse(active_id)
        budget_release = budget_line.budget_id.budget_level_id.budget_release
        if budget_release != 'manual_line':
            raise ValidationError(_('Manual budget released not allowed!'))
        release_result = {}
        release_result.update({budget_line.id: self.amount_to_release})
        budget_line.release_budget_line(release_result)
