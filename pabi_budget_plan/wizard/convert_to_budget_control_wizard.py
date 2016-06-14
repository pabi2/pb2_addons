# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ConvertToBudgetControlWizard(models.TransientModel):
    _name = "convert.to.budget.control.wizard"

    @api.multi
    def convert_to_budget_control(self):
        active_model = self._context.get('active_model', False)
        active_ids = self._context.get('active_ids', False)
        if active_model not in ('budget.plan.unit'):
            raise ValidationError(
                _('This budget model is not supported: %s') % (active_model,))
        if active_model == 'budget.plan.unit':
            self.env[active_model].convert_plan_to_budget_control(active_ids)
