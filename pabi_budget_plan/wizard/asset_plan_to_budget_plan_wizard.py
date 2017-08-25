# -*- coding: utf-8 -*-
from openerp import models, api


class AssetPlanToBudgetPlanWizard(models.TransientModel):
    _name = "asset.plan.to.budget.plan.wizard"

    @api.multi
    def asset_plan_to_budget_plan(self):
        active_ids = self._context.get('active_ids', False)
        asset_plans = self.env['invest.asset.plan'].browse(active_ids)
        asset_plans.convert_to_budget_plan()
