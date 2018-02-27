# -*- coding: utf-8 -*-
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
        _DICT = {
            'unit_base': (
                'budget.plan.unit',
                'pabi_budget_plan.action_budget_plan_unit_view'),
            'project_base': (
                'budget.plan.project',
                'pabi_budget_plan.action_budget_plan_project_view'),
            'personnel': (
                'budget.plan.personnel',
                'pabi_budget_plan.action_budget_plan_personnel_view'),
            'invest_asset': (
                'invest.asset.plan',  # Asset Plan
                'pabi_budget_plan.action_invest_asset_plan_view'),
            'invest_construction': (
                'budget.plan.invest.construction',  # Asset Plan
                'pabi_budget_plan.'
                'action_budget_plan_invest_construction_view'),
        }
        if self.chart_view not in _DICT.keys():
            raise ValidationError(_('Selected budget view is not valid!'))
        fiscalyear_id = self.fiscalyear_id.id
        model = _DICT[self.chart_view][0]
        view = _DICT[self.chart_view][1]
        plan_ids = self.env[model].generate_plans(fiscalyear_id=fiscalyear_id)
        action = self.env.ref(view)
        result = action.read()[0]
        dom = [('id', 'in', plan_ids)]
        result.update({'domain': dom})
        return result
