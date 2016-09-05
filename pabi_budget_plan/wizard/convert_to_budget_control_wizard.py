# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import ValidationError


class ConvertToBudgetControlWizard(models.TransientModel):
    _name = "convert.to.budget.control.wizard"

    @api.multi
    def convert_to_budget_control(self):
        # TODO: Pending to delete (it won't be called)
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        if active_model not in ('budget.plan.unit',
                                'budget.plan.personnel'):
            raise ValidationError(
                _('This budget model is not supported: %s') % (active_model,))
        self.env[active_model].convert_plan_to_budget_control(active_id)
