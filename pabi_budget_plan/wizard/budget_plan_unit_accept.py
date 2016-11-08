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
            if plan.state in ('submit'):
                plan.button_accept()
            else:
                raise UserError(
                    _("Selected budget plan cannot be approved\
                    as they are not in 'Submitted' state."))

class BudgetPlanUnitVerify(models.TransientModel):
    _name = "budget.plan.unit.verify"

    @api.multi
    def verify_budget_plan(self):
        active_ids = self._context.get('active_ids', [])
        plan_ids = self.env['budget.plan.unit'].browse(active_ids)
        for plan in plan_ids:
            if plan.state in ('accept'):
                plan.button_approve()
            else:
                raise UserError(
                    _("Selected budget plan cannot be verify\
                    as they are not in 'Approved' state."))

class BudgetPlanUnitAccepteCorp(models.TransientModel):
    _name = "budget.plan.unit.accept.corp"

    @api.multi
    def corp_accept_budget_plan(self):
        active_ids = self._context.get('active_ids', [])
        plan_ids = self.env['budget.plan.unit'].browse(active_ids)
        for plan in plan_ids:
            if plan.state in ('approve'):
                plan.button_accept_corp()
            else:
                raise UserError(
                    _("Selected budget plan cannot be verify\
                    as they are not in 'Verified' state."))
            
