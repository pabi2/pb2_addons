# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_template import BudgetPlanCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon


class BudgetPlanPersonnel(BudgetPlanCommon, models.Model):
    _name = 'budget.plan.personnel'
    _inherits = {'budget.plan.template': 'template_id'}
    _description = "Personnel Budget - Budget Plan"

    template_id = fields.Many2one(
        'budget.plan.template',
        required=True,
        ondelete='cascade',
    )
    # TEMP
    plan_line_ids = fields.One2many(
        'budget.plan.personnel.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.personnel.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        readonly=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.personnel.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        readonly=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    # plan_summary_revenue_line_ids = fields.One2many(
    #     'budget.plan.personnel.summary',
    #     'plan_id',
    #     string='Summary by Activity Group',
    #     domain=[('budget_method', '=', 'revenue')],
    #     readonly=True,
    #     help="Summary by Activity Group View",
    # )
    # plan_summary_expense_line_ids = fields.One2many(
    #     'budget.plan.personnel.summary',
    #     'plan_id',
    #     string='Summary by Activity Group',
    #     domain=[('budget_method', '=', 'expense')],
    #     readonly=True,
    #     help="Summary by Activity Group View",
    # )
    planned_revenue = fields.Float(
        string='Total Revenue Plan',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_expense = fields.Float(
        string='Total Expense Plan',
        compute='_compute_planned_overall',
        store=True,
    )
    planned_overall = fields.Float(
        string='Total Planned',
        compute='_compute_planned_overall',
        store=True,
    )

    @api.onchange('personnel_costcenter_id')
    def _onchange_personnel_costcenter_id(self):
        self.section_id = self.personnel_costcenter_id.section_id

    # Call inherited methods
    @api.multi
    def unlink(self):
        for rec in self:
            rec.plan_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPlanPersonnel, self).unlink()

    @api.model
    def convert_plan_to_budget_control(self, active_id):
        head_src_model = self.env['budget.plan.personnel']
        line_src_model = self.env['budget.plan.personnel.line']
        return self._convert_plan_to_budget_control(active_id,
                                                    head_src_model,
                                                    line_src_model)


class BudgetPlanPersonnelLine(ActivityCommon, models.Model):
    _name = 'budget.plan.personnel.line'
    _inherits = {'budget.plan.line.template': 'template_id'}
    _description = "Personnel Budget - Budget Plan Line"

    plan_id = fields.Many2one(
        'budget.plan.personnel',
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
        res = super(BudgetPlanPersonnelLine, self).create(vals)
        res.write({'chart_view': res.plan_id.chart_view,
                   'fiscalyear_id': res.plan_id.fiscalyear_id.id})
        return res

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPlanPersonnelLine, self).unlink()
