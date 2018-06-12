# -*- coding: utf-8 -*-
from openerp import api, models


class ResProjectBudgetPlan(models.Model):
    _inherit = 'res.project.budget.plan'

    @api.model
    def sync_project_budget_plan(self):
        """ Find any budget plan  """
        BudgetPlan = self.env['res.project.budget.plan']
        plans = BudgetPlan.search([('synced', '=', False)])
        print plans
        projects = plans.mapped('project_id')
        for project in projects:
            try:
                project.sync_budget_control()
                self._cr.commit()
                print project.code
            except Exception:
                pass
