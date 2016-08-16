# -*- coding: utf-8 -*-
from openerp import models, api


class AssetPlanToBudgetPlanWizard(models.TransientModel):
    _name = "asset.plan.to.budget.plan.wizard"

    @api.multi
    def asset_plan_to_budget_plan(self):
        active_ids = self._context.get('active_ids', False)
        self.env['invest.asset.plan'].convert_to_budget_plan(active_ids)
