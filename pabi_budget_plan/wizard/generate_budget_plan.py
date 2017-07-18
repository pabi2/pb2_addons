# -*- coding: utf-8 -*-
import time
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import CHART_VIEW_LIST


class GenerateBudgetPlan(models.TransientModel):
    _name = "generate.budget.plan"

    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        # domain=[('date_start', '>', time.strftime('%Y-%m-%d'))],
        required=True,
    )

    @api.multi
    def action_generate_budget_plan(self):
        self.ensure_one()
        plan_ids = []
        fiscalyear_id = self.fiscalyear_id.id
        if self.chart_view == 'unit_base':
            UnitBase = self.env['budget.plan.unit']
            plan_ids = UnitBase.generate_plans(fiscalyear_id=fiscalyear_id)
        elif self.chart_view == 'project_base':
            ProjectBase = self.env['budget.plan.project']
            plan_ids = ProjectBase.generate_plans(fiscalyear_id=fiscalyear_id)
        elif self.chart_view == 'personnel':
            Personnel = self.env['budget.plan.personnel']
            plan_ids = Personnel.generate_plans(fiscalyear_id=fiscalyear_id)
        else:
            raise ValidationError(_('Selected budget view is not valid!'))
        action = self.env.ref('pabi_budget_plan.action_budget_plan_unit_view')
        result = action.read()[0]
        dom = [('id', '=', plan_ids)]
        result.update({'domain': dom})
        return result
