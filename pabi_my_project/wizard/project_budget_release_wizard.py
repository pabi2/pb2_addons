# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class ProjectBudgetReleaseWizard(models.TransientModel):
    _name = "project.budget.release.wizard"

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
        BudgetLine = self.env[active_model]
        budget_line = BudgetLine.search([('id', '=', active_id)])

        planned_amount = budget_line.planned_amount
        if not planned_amount:
            self.progress = 0.0
        else:
            self.progress = self.amount_to_release / planned_amount * 100

    @api.model
    def default_get(self, fields):
        res = super(ProjectBudgetReleaseWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        budget_line = self.env[active_model].browse(active_id)
        res['amount_to_release'] = budget_line.released_amount
        return res

    @api.multi
    def do_release(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        budget_line = self.env[active_model].browse(active_id)
        if self.amount_to_release > budget_line.planned_amount:
            raise ValidationError(
                _('Release amount exceed planned amount!'))
        budget_line.write({'released_amount': self.amount_to_release})
        budget_line.project_id._trigger_auto_sync()
