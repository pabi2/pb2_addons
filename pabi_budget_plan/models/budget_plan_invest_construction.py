# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_template import BudgetPlanCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon


class BudgetPlanInvestConstruction(BudgetPlanCommon, models.Model):
    _name = 'budget.plan.invest.construction'
    _inherits = {'budget.plan.template': 'template_id'}
    _description = "Investment Construction Budget - Budget Plan"

    template_id = fields.Many2one(
        'budget.plan.template',
        required=True,
        ondelete='cascade',
    )
    plan_line_ids = fields.One2many(
        'budget.plan.invest.construction.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=False,
    )
    planned_overall = fields.Float(
        string='Budget Plan',
        compute='_compute_planned_overall',
        store=True,
    )

    # Call inherited methods
    @api.multi
    def unlink(self):
        for rec in self:
            rec.plan_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPlanInvestConstruction, self).unlink()

    @api.model
    def convert_plan_to_budget_control(self, active_ids):
        head_src_model = self.env['budget.plan.invest.construction']
        line_src_model = self.env['budget.plan.invest.construction.line']

        self._convert_plan_to_budget_control(active_ids,
                                             head_src_model,
                                             line_src_model)


class BudgetPlanInvestConstructionLine(ActivityCommon, models.Model):
    _name = 'budget.plan.invest.construction.line'
    _inherits = {'budget.plan.line.template': 'template_id'}
    _description = "Investment Construction Budget - Budget Plan Line"

    plan_id = fields.Many2one(
        'budget.plan.invest.construction',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    template_id = fields.Many2one(
        'budget.plan.line.template',
        required=True,
        ondelete='cascade',
    )

    @api.model
    def create(self, vals):
        res = super(BudgetPlanInvestConstructionLine, self).create(vals)
        res.write({'chart_view': res.plan_id.chart_view,
                   'fiscalyear_id': res.plan_id.fiscalyear_id.id})
        return res

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPlanInvestConstructionLine, self).unlink()
