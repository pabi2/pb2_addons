# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import Warning as UserError


class BudgetPlanUnitAccept(models.TransientModel):
    _name = "budget.plan.unit.accept"

    @api.multi
    def accept_budget_plan(self):
        active_ids = self._context.get('active_ids', [])
        plan_ids = self.env['budget.plan.unit'].browse(active_ids)
        for plan in plan_ids:
            if plan.state not in ('submit'):
                raise UserError(
                    _("Selected budget plan cannot be accepted\
                    as they are not in 'Submitted' state."))
            plan.button_accept()
