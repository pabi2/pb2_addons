# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
# from openerp.addons.document_status_history.models.document_history import \
#     LogCommon


class BudgetPlanProject(BPCommon, models.Model):
    _name = 'budget.plan.project'
    _inherit = ['mail.thread']
    _description = "Project - Budget Plan"
    _order = 'id desc'

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        track_visibility='onchange',
    )
    # Project Only
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
    # Select Dimension - Project
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        required=True,
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        related='program_id.program_group_id',
        readonly=True,
        store=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        related='program_id.functional_area_id',
        readonly=True,
        store=True,
    )
    _sql_constraints = [
        ('uniq_plan', 'unique(program_id, fiscalyear_id)',
         'Duplicated budget plan for the same program is not allowed!'),
    ]

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.program', vals['program_id'])
        vals.update({'name': name})
        return super(BudgetPlanProject, self).create(vals)

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('program_id')._ids
        # Find Programs
        programs = self.env['res.program'].search([('id', 'not in', _ids)])
        plan_ids = []
        for program in programs:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'program_id': program.id,
                                'user_id': False})
            plan_ids.append(plan.id)
        return plan_ids

    @api.multi
    def convert_to_budget_control(self):
        """ Create a budget control from budget plan """
        self.ensure_one()
        head_src_model = self.env['budget.plan.project']
        line_src_model = self.env['budget.plan.project.line']
        budget = self._convert_plan_to_budget_control(self.id,
                                                      head_src_model,
                                                      line_src_model)
        return budget


class BudgetPlanProjectLine(BPLMonthCommon, ActivityCommon, models.Model):
    _name = 'budget.plan.project.line'
    _description = "Project - Budget Plan Line"

    # COMMON
    chart_view = fields.Selection(
        default='project_base',  # Project
    )
    plan_id = fields.Many2one(
        'budget.plan.project',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # Extra
    program_id = fields.Many2one(
        related='plan_id.program_id',
        store=True,
        readonly=True,
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

    # Required for updating dimension
    @api.model
    def create(self, vals):
        res = super(BudgetPlanProjectLine, self).create(vals)
        if not self._context.get('MyModelLoopBreaker', False):
            res.update_related_dimension(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(BudgetPlanProjectLine, self).write(vals)
        if not self._context.get('MyModelLoopBreaker', False):
            self.update_related_dimension(vals)
        return res
    # ---------
