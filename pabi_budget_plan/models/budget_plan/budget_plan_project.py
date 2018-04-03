# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon
# , PrevFYCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
# from openerp.addons.document_status_history.models.document_history import \
#     LogCommon


class BudgetPlanProject(BPCommon, models.Model):
    _name = 'budget.plan.project'
    _inherit = ['mail.thread']
    _description = "Project - Budget Plan"
    _order = 'fiscalyear_id desc, id desc'

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.project.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
        readonly=True,
        states={'1_draft': [('readonly', False)]},
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
    # Select Dimension - Project
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        required=True,
        readonly=True,
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
    # Master Datas
    master_project_group_ids = fields.Many2many(
        'res.project.group',
        string='Project Group',
        compute='_compute_master_project_group_ids'
    )
    master_strategy_ids = fields.Many2many(
        'project.nstda.strategy',
        sring='Strategy Master Data',
        compute='_compute_master_strategy_ids',
    )
    master_subprogram_ids = fields.Many2many(
        'project.subprogram',
        string='Subprogram',
        compute='_compute_master_subprogram_ids',
    )
    master_mission_ids = fields.Many2many(
        'res.mission',
        sring='Mission Master Data',
        compute='_compute_master_mission_ids',
    )
    master_project_type_ids = fields.Many2many(
        'project.type',
        string='Project Type',
        compute='_compute_master_project_type_ids'
    )
    master_operation_ids = fields.Many2many(
        'project.operation',
        string='Project Operation',
        compute='_compute_master_operation_ids'
    )
    master_program_ids = fields.Many2many(
        'res.program',
        string='Program',
        compute='_compute_master_program_ids'
    )
    master_fund_type_ids = fields.Many2many(
        'project.fund.type',
        string='Fund Type',
        compute='_compute_master_fund_type_ids'
    )

    _sql_constraints = [
        ('uniq_plan', 'unique(program_id, fiscalyear_id)',
         'Duplicated budget plan for the same program is not allowed!'),
    ]

    @api.multi
    def _compute_master_project_group_ids(self):
        PG = self.env['res.project.group']
        for rec in self:
            rec.master_project_group_ids = PG.search([]).ids

    @api.multi
    def _compute_master_strategy_ids(self):
        Strategy = self.env['project.nstda.strategy']
        for rec in self:
            rec.master_strategy_ids = Strategy.search([]).ids

    @api.multi
    def _compute_master_subprogram_ids(self):
        Subprogram = self.env['project.subprogram']
        for rec in self:
            rec.master_subprogram_ids = Subprogram.search(
                [('program_id', '=', rec.program_id.id)]).ids

    @api.multi
    def _compute_master_mission_ids(self):
        M = self.env['res.mission']
        for rec in self:
            rec.master_mission_ids = M.search([]).ids

    @api.multi
    def _compute_master_project_type_ids(self):
        PT = self.env['project.type']
        for rec in self:
            rec.master_project_type_ids = PT.search([]).ids

    @api.multi
    def _compute_master_operation_ids(self):
        Operation = self.env['project.operation']
        for rec in self:
            rec.master_operation_ids = Operation.search([]).ids

    @api.multi
    def _compute_master_program_ids(self):
        Program = self.env['res.program']
        for rec in self:
            rec.master_program_ids = Program.search([]).ids

    @api.multi
    def _compute_master_fund_type_ids(self):
        FundType = self.env['project.fund.type']
        for rec in self:
            rec.master_fund_type_ids = FundType.search([]).ids

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.program', res_id=vals['program_id'])
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
        programs = self.env['res.program'].search([('id', 'not in', _ids),
                                                   ('special', '=', False)])
        plan_ids = []
        for program in programs:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'program_id': program.id,
                                'user_id': False})
            plan_ids.append(plan.id)

        # Special for Project Based, also create budget control too
        budget_ids = self.env['account.budget'].\
            generate_project_base_controls(fiscalyear_id)

        # For project, do auto activate
        self.env['account.budget'].browse(budget_ids).budget_done()
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

    @api.multi
    def _validate_header(self, vals):
        """ Make sure that, some header fields must not change """
        nochange_fields = {'fiscalyear_id': _('Fiscal Year'),
                           'program_id': _('Program'), }
        for field in nochange_fields.keys():
            if field in vals:
                for rec in self:
                    if rec[field].id != vals[field]:
                        raise ValidationError(
                            _('You can not change header field %s.' %
                              nochange_fields[field]))

    @api.multi
    def write(self, vals):
        self._validate_header(vals)
        return super(BudgetPlanProject, self).write(vals)


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
    code = fields.Char(
        string='Project Code',
    )
    name = fields.Char(
        string='Project Name',
    )
    program_id = fields.Many2one(
        related='plan_id.program_id',
        store=True,
        readonly=True,
    )
    section_program_id = fields.Many2one(
        related='plan_id.program_id.section_program_id',
        store=True,
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        required=False,  # Change from BPLCommon to required=False
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    # Project Based Specific
    c_or_n = fields.Selection(
        [('continue', u'ต่อเนื่อง'),
         ('new', u'ใหม่')],
        string='C/N',
        default='new',
    )
    nstda_strategy_id = fields.Many2one(
        'project.nstda.strategy',
        string='NSTDA Strategy',
    )
    # Budget Control
    planned = fields.Float(  # cur_current_budget
        string='Current Budget',
        readonly=True,
        help="This FY Budget Plan (what is different with budget released?)",
    )
    released = fields.Float(  # cur_release_budget
        string='Current Released',
        readonly=True,
        help="This FY Budget Released",
    )
    all_commit = fields.Float(  # cur_commit_budget
        string='Current All Commit',
        readonly=True,
        help="This FY Total Commitment",
    )
    actual = fields.Float(  # cur_actual
        string='Current Actual',
        readonly=True,
        help="This FY actual amount",
    )
    balance = fields.Float(  # cur_remaining_budget
        string='Remaining Budget',
        readonly=True,
        help="This FY Budget Remaining"
    )
    est_commit = fields.Float(  # cur_estimated_commitment
        string='Estimated Commitment',
        readonly=True,
        help="Next fiscalyear commitment PO Invoice Plan",
    )
    # Project Detail
    amount_before = fields.Float(
        string='Before FY1',
    )
    amount_fy1 = fields.Float(
        string='FY1',
    )
    amount_fy2 = fields.Float(
        string='FY2',
    )
    amount_fy3 = fields.Float(
        string='FY3',
    )
    amount_fy4 = fields.Float(
        string='FY4',
    )
    amount_beyond = fields.Float(
        string='FY5 ++',
    )
    amount_overall = fields.Float(
        string='Overall',
    )
    # For internal charge
    amount_before_internal = fields.Float(
        string='Before FY1 (I)',
    )
    amount_fy1_internal = fields.Float(
        string='FY1 (I)',
    )
    amount_fy2_internal = fields.Float(
        string='FY2 (I)',
    )
    amount_fy3_internal = fields.Float(
        string='FY3 (I)',
    )
    amount_fy4_internal = fields.Float(
        string='FY4 (I)',
    )
    amount_beyond_internal = fields.Float(
        string='FY5 (I) ++',
    )
    amount_overall_internal = fields.Float(
        string='Overall (Internal)',
    )
    # --
    revenue_budget = fields.Float(
        string='Revenue Budget',
    )
    overall_revenue_plan = fields.Float(
        string='Overall Revenue Plan',
    )
    project_kind = fields.Selection(
        [('research', 'Research'),
         ('non_research', 'Non Research'),
         ('management', 'Management Program/Cluster'),
         ('construction', 'Construction'), ],
        related='project_type_id.project_kind',
        string='Project Kind',
        store=True,
    )
    operation_id = fields.Many2one(
        'project.operation',
        string='Operation',
    )
    fund_type_id = fields.Many2one(
        'project.fund.type',
        string='Fund Type',
    )
    subprogram_id = fields.Many2one(
        'project.subprogram',
        string='Subprogram',
        domain="[('program_id', '=', program_id)]",
    )
    project_type_id = fields.Many2one(
        'project.type',
        string='Project Type',
    )
    pm_employee = fields.Char(
        string='Project Manager',
    )
    section = fields.Char(
        string='Section',
    )
    division = fields.Char(
        string='Division',
    )
    org = fields.Char(
        string='Org',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    project_duration = fields.Integer(
        string='Duration',
    )
    project_status = fields.Char(
        string='Project Status',
    )
    analyst_employee = fields.Char(
        string='Project Analyst',
    )
    ref_program_id = fields.Many2one(
        'res.program',
        string='Program Reference',
    )
    proposal_program_id = fields.Many2one(
        'res.program',
        string='Proposal Program',
    )
    external_fund_type = fields.Selection(
        [('government', '1. ภาครัฐ'),
         ('private', '2. ภาคเอกชน'),
         ('oversea', '3. ต่างประเทศ')],
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
    overall_revenue = fields.Float(
        string='Accum. Revenue',
    )
    current_revenue = fields.Float(
        string='Current Year Revenue',
    )
    overall_expense_budget = fields.Float(
        string='Overall Expense Budget',
    )
    overall_actual = fields.Float(
        string='Accum. Expense',
    )
    overall_commit = fields.Float(
        string='Accum. Commitment',
    )
    overall_expense_balance = fields.Float(
        string='Remaining Expense Budget',
    )

    # Required for updating dimension
    # FIND ONLY WHAT IS NEED AND USE related field.

    @api.multi
    def edit_project(self):
        self.ensure_one()
        action = self.env.ref('pabi_budget_plan.'
                              'action_budget_plan_project_line_view')
        result = action.read()[0]
        view = self.env.ref('pabi_budget_plan.'
                            'view_budget_plan_project_line_form')
        result.update(
            {'res_id': self.id,
             'view_id': False,
             'view_mode': 'form',
             'views': [(view.id, 'form')],
             'context': False, })
        return result


# class BudgetPlanProjectPrevFYView(PrevFYCommon, models.Model):
#     """ Prev FY Performance view, must named as [model]+perv.fy.view """
#     _name = 'budget.plan.project.prev.fy.view'
#     _auto = False
#     _description = 'Prev FY budget performance for project base'
#     # Extra variable for this view
#     _chart_view = 'project_base'
#     _ex_view_fields = ['program_id', 'project_id']  # Each line
#     _ex_domain_fields = ['program_id']  # Each plan is by this domain
#     # TODO: what contion that we will not retrieve previous year data?
#     # _ex_active_domain = [('project_id.state', '=', 'approve')]
#     _ex_active_domain = []
#     _filter_fy = 1  # Will the result of his view focus on prev fy only
#
#     program_id = fields.Many2one(
#         'res.program',
#         string='Program',
#         readonly=True,
#     )
#     project_id = fields.Many2one(
#         'res.project',
#         string='Project',
#         readonly=True,
#     )
#
#     @api.multi
#     def _prepare_prev_fy_lines(self):
#         """ Given search result from this view, prepare lines tuple """
#         plan_lines = []
#         plan_fiscalyear_id = self._context.get('plan_fiscalyear_id')
#         Project = self.env['res.project']
#         ProjectLine = self.env['budget.plan.project.line']
#         project_fields = set(Project._fields.keys())
#         plan_line_fields = set(ProjectLine._fields.keys())
#         common_fields = list(project_fields & plan_line_fields)
#         for rec in self:
#             # Get commitment other than, the previous year.
#             expenses = rec.project_id.monitor_expense_ids
#             revenues = rec.project_id.monitor_revenue_ids
#
#             all_actual_expense = sum(expenses.mapped('amount_actual'))
#             all_actual_revenue = sum(revenues.mapped('amount_actual'))
#
#             next_fy_ex = expenses.filtered(
#                 lambda l: l.fiscalyear_id.id == plan_fiscalyear_id)
#             next_fy_commit = sum(next_fy_ex.mapped('amount_pr_commit') +
#                                  next_fy_ex.mapped('amount_po_commit') +
#                                  next_fy_ex.mapped('amount_exp_commit'))
#
#             ytd_ex = expenses.filtered(
#                 lambda l: l.fiscalyear_id.date_start <=
#                 rec.fiscalyear_id.date_start)
#             ytd_commit = sum(ytd_ex.mapped('amount_pr_commit') +
#                              ytd_ex.mapped('amount_po_commit') +
#                              ytd_ex.mapped('amount_exp_commit'))
#
#             current_actual_revenue = sum(revenues.filtered(
#                 lambda l: l.fiscalyear_id == rec.fiscalyear_id
#             ).mapped('amount_actual'))
#
#             # 1) Begins
#             val = {'c_or_n': 'continue',
#                    'code': rec.project_id.code,
#                    'name': rec.project_id.name,
#                    'fund_id': rec.fund_id.id,
#                    # some misc fields
#                    'pm_employee': rec.project_id.pm_employee_id.name,
#                  'analyst_employee': rec.project_id.analyst_employee_id.name,
#                    'section': rec.project_id.pm_section_id.name,
#                    'division': rec.project_id.owner_division_id.name,
#                    'org': rec.project_id.org_id.name, }
#             # 2) Project Info
#             for field in common_fields:
#                 if field in rec.project_id and \
#                         field not in ['id', '__last_update',
#                                       'write_uid', 'write_date',
#                                       'create_uid', 'create_date',
#                                       'state',
#                                     # Related fields should not get updated,
#                                       # it unnecessary slow
#                                       'program_id', 'section_program_id',
#                                       'owner_division_id',
#                                       ]:
#                     try:
#                         val[field] = rec.project_id[field].id
#                     except:
#                         val[field] = rec.project_id[field]
#             # Calc from PABI2 monitoring views
#             # 3) Overall
#             val.update({'overall_revenue': all_actual_revenue,
#                         'current_revenue': current_actual_revenue,
#                         'overall_actual': all_actual_expense,
#                         'overall_commit': ytd_commit,
#                         'overall_expense_balance':
#                         (val.get('overall_expense_budget', 0.0) -
#                          all_actual_expense - ytd_commit), })
#             # 4) Current Year
#             val.update({
#                 'planned': rec.planned,
#                 'released': rec.released,
#                 'all_commit': rec.all_commit,
#                 'actual': rec.actual,
#                 'balance': rec.balance,
#                 'est_commit': next_fy_commit,  # from PO invoice plan
#             })
#             plan_lines.append((0, 0, val))
#         return plan_lines
