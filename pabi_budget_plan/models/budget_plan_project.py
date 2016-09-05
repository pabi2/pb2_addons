# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_template import BudgetPlanCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon


class BudgetPlanProject(BudgetPlanCommon, models.Model):
    _name = 'budget.plan.project'
    _inherits = {'budget.plan.template': 'template_id'}
    _description = "Project Based - Budget Plan"

    template_id = fields.Many2one(
        'budget.plan.template',
        required=True,
        ondelete='cascade',
    )
    plan_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=False,
        readonly=True,
    )
    project_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
    )
    performance_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
    )
    planned_overall = fields.Float(
        string='Budget Plan',
        compute='_compute_planned_overall',
        store=True,
    )

    @api.onchange('program_id')
    def _onchange_program_id(self):
        self.program_group_id = self.program_id.program_group_id
        self.functional_area_id = self.program_id.functional_area_id

    # Call inherited methods
    @api.multi
    def unlink(self):
        for rec in self:
            rec.plan_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPlanProject, self).unlink()


class BudgetPlanProjectLine(ActivityCommon, models.Model):
    _name = 'budget.plan.project.line'
    _inherits = {'budget.plan.line.template': 'template_id'}
    _description = "Project Based - Budget Plan Line"

    plan_id = fields.Many2one(
        'budget.plan.project',
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
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    # Project Based Specific
    c_or_n = fields.Selection(
        [('continue', 'Continue'),
         ('new', 'New')],
        string='C/N',
        default='new',
    )
    project_kind = fields.Selection(
        [('research', 'Research'),
         ('non_research', 'Non-Research')],
        string='Research / Non-Research',
    )
    project_objective = fields.Char(
        string='Objective',
    )
    project_type = fields.Char(
        string='Project Type',
    )
    manager_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
    )
    date_from = fields.Date(
        string='Start Date',
    )
    date_to = fields.Date(
        string='End Date',
    )
    project_duration = fields.Integer(
        string='Duration',
    )
    project_status = fields.Char(
        string='Project Status',
    )
    analyst_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Analyst',
    )
    ref_program_id = fields.Many2one(
        'res.program',
        string='Program Reference',
    )
    external_fund_type = fields.Selection(
        [('government', 'Government'),
         ('private', 'Private Organization'),
         ('oversea', 'Oversea')],
        string='External Fund Type',
    )
    external_fund_name = fields.Char(
        string='External Fund Name',
    )
    priority = fields.Char(
        string='Priority',
    )
    # Project Performance (myPerformance)
    pfm_publications = fields.Integer(
        string='Publication',
    )
    pfm_patents = fields.Integer(
        string='Patent',
    )
    pfm_petty_patents = fields.Integer(
        string='Petty Patent',
    )
    pfm_copyrights = fields.Integer(
        string='Copy Right',
    )
    pfm_trademarks = fields.Integer(
        string='Trademark',
    )
    pfm_plant_varieties = fields.Integer(
        string='Plant Varieties',
    )
    pfm_laboratory_prototypes = fields.Integer(
        string='Laboratory Prototype',
    )
    pfm_field_prototypes = fields.Integer(
        string='Field Prototype',
    )
    pfm_commercial_prototypes = fields.Integer(
        string='Commercial Prototype',
    )
    pfm_revenue_budget = fields.Float(
        string='Revenue Budget',
    )
    pfm_revenue_overall_plan = fields.Float(
        string='Overall Revenue Plan',
    )
    pfm_revenue_accum = fields.Float(
        string='Accum. Revenue',
    )
    pfm_revenue_current_year = fields.Float(
        string='Current Year Revenue',
    )
    pfm_expense_overall_budget = fields.Float(
        string='Overall Expense Budget',
    )
    pfm_expense_accum = fields.Float(
        string='Accum. Expense',
    )
    pfm_commitment_accum = fields.Float(
        string='Accum. Commitment',
    )
    pfm_expense_remaining_budget = fields.Float(
        string='Remaining Expense Budget',
    )
    # Budget Control
    cur_current_budget = fields.Float(
        string='Current Budget',
    )
    cur_release_budget = fields.Float(
        string='Release Budget',
    )
    cur_commit_budget = fields.Float(
        string='Commit Budget',
    )
    cur_actual = fields.Float(
        string='Actual',
    )
    cur_remaining_budget = fields.Float(
        string='Remaining Budget',
    )
    cur_estimated_commitment = fields.Float(
        string='Estimated Commitment',
    )
    fy1 = fields.Float(
        string='FY1',
    )
    fy2 = fields.Float(
        string='FY2',
    )
    fy3 = fields.Float(
        string='FY3',
    )
    fy4 = fields.Float(
        string='FY4',
    )
    fy5 = fields.Float(
        string='FY5',
    )
    total = fields.Float(
        string='Total',
    )

    @api.model
    def create(self, vals):
        res = super(BudgetPlanProjectLine, self).create(vals)
        res.write({'chart_view': res.plan_id.chart_view,
                   'fiscalyear_id': res.plan_id.fiscalyear_id.id})
        return res

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPlanProjectLine, self).unlink()
