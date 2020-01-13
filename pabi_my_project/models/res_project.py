# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp import models, api, fields, _
from openerp import tools
from openerp.exceptions import ValidationError
from openerp.addons.document_status_history.models.document_history import \
    LogCommon
from openerp.addons.pabi_base.models.res_common import ResCommon
from openerp.tools.float_utils import float_compare


MY_PROJECT_STATES = [('draft', 'Draft'),
                     ('approve', 'Approved'),
                     ('delete', 'Deleted'),
                     ('cancel', 'Cancelled'),
                     ('close', 'Closed'),
                     ]


class ResProgram(models.Model):
    _inherit = 'res.program'

    myproject_use = fields.Boolean(
        string='myProject Use',
        default=False,
    )


class ResProject(LogCommon, models.Model):
    _inherit = 'res.project'

    state = fields.Selection(
        MY_PROJECT_STATES,
        string='Status',
        related='project_status.res_project_state',
        store=True,
        readonly=True,
    )
    lock_release = fields.Boolean(
        string='Lock Budget Release',
        default=False,
        help="If lock_budget is checked, release budget is not allowed",
    )
    date_start = fields.Date(
        string='Start Date for Spending',
    )
    date_approve = fields.Date(
        string='Approved Date',
    )
    date_end = fields.Date(
        string='End Date for Spending',
    )
    project_duration = fields.Integer(
        string='Project Duration',
    )
    project_status = fields.Many2one(
        'myproject.status',
        string='Project Status',
    )
    contract_duration = fields.Integer(
        string='Contract Duration',
    )
    proposal_status = fields.Many2one(
        'proposal.status',
        string='Proposal Status',
    )
    project_date_end_proposal = fields.Date(
        string='Project End Date (by proposal)',
    )
    project_date_close_cond = fields.Date(
        string='Project Close Date (Condition)',
    )
    project_date_start = fields.Date(
        string='Project start Date',
    )
    project_date_end = fields.Date(
        string='Project End Date',
    )
    project_date_close = fields.Date(
        string='Project Close Date (Complete)',
    )
    project_date_terminate = fields.Date(
        string='Project Terminate Date',
    )
    contract_date_start = fields.Date(
        string='Contract start Date',
    )
    contract_date_end = fields.Date(
        string='Contract End Date',
    )
    pm_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
        required=True,
    )
    pm_section_id = fields.Many2one(
        'res.section',
        string='Project Manager Section',
        related='pm_employee_id.section_id',
        readonly=True,
    )
    external_pm = fields.Char(
        string='External PM',
        size=500,
    )
    owner_division_id = fields.Many2one(
        'res.division',
        string='Project Division',
        related='pm_employee_id.section_id.division_id',
        readonly=True,
    )
    analyst_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Analyst',
        required=True,
    )
    analyst_section_id = fields.Many2one(
        'res.section',
        string='Project Analyst Section',
        related='analyst_employee_id.section_id',
        readonly=True,
    )
    ref_program_id = fields.Many2one(
        'res.program',
        string='Program Reference',
    )
    target_program_id = fields.Many2one(
        'program.target',
        string='Program Target',
    )
    proposal_program_id = fields.Many2one(
        'res.program',
        string='Current Program',
    )
    external_fund_type = fields.Selection(
        [('government', '1. ภาครัฐ'),
         ('private', '2. ภาคเอกชน'),
         ('oversea', '3. ต่างประเทศ')],
        string='External Fund Type',
    )
    external_fund_name = fields.Char(
        string='External Fund Name',
        size=500,
    )
    priority = fields.Char(
        string='Priority',
        size=10,
    )
    budget_plan_ids = fields.One2many(
        'res.project.budget.plan',
        'project_id',
        string='Budget Lines',
    )
    budget_plan_expense_ids = fields.One2many(
        'res.project.budget.plan',
        'project_id',
        domain=[('budget_method', '=', 'expense')],
        string='Budget Expense Lines',
    )
    budget_plan_revenue_ids = fields.One2many(
        'res.project.budget.plan',
        'project_id',
        domain=[('budget_method', '=', 'revenue')],
        string='Budget Revenue Lines',
    )
    budget_release_ids = fields.One2many(
        'res.project.budget.release',
        'project_id',
        string='Budget Release History',
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        'res_project_fiscalyear_rel', 'project_id', 'fiscalyear_id',
        string='Related Fiscal Years',
        compute='_compute_fiscalyear_ids',
        store=True,
        help="All related fiscal years for this project"
    )
    budget_count = fields.Integer(
        string='Budget Control Count',
        compute='_compute_budget_count',
    )
    budget_to_sync_count = fields.Integer(
        string='Budget Need Sync Count',
        compute='_compute_budget_to_sync_count',
    )
    summary_ids = fields.One2many(
        'res.project.budget.summary',
        'project_id',
        string='Project Summary',
        readonly=True,
    )
    summary_expense_ids = fields.One2many(
        'res.project.budget.summary',
        'project_id',
        string='Project Summary',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
    )
    summary_revenue_ids = fields.One2many(
        'res.project.budget.summary',
        'project_id',
        string='Project Summary',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
    )
    member_ids = fields.One2many(
        'res.project.member',
        'project_id',
        string='Project Member',
        copy=False,
    )
    nstda_strategy_id = fields.Many2one(
        'project.nstda.strategy',
        string='NSTDA Strategy',
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
    # Project Detail    # Project Detail
    amount_before = fields.Float(
        string='Before FY1',
        compute='_compute_amount_fy',
    )
    amount_fy1 = fields.Float(
        string='FY1',
        compute='_compute_amount_fy',
        help="FY1 means next fiscalyear, based on current date",
    )
    amount_fy2 = fields.Float(
        string='FY2',
        compute='_compute_amount_fy',
    )
    amount_fy3 = fields.Float(
        string='FY3',
        compute='_compute_amount_fy',
    )
    amount_fy4 = fields.Float(
        string='FY4',
        compute='_compute_amount_fy',
    )
    amount_beyond = fields.Float(
        string='FY5 and Beyond',
        compute='_compute_amount_fy',
    )
    amount_before_internal = fields.Float(
        string='Before FY1 (I)',
        compute='_compute_amount_fy',
    )
    amount_fy1_internal = fields.Float(
        string='FY1 (I)',
        compute='_compute_amount_fy',
        help="FY1 means next fiscalyear, based on current date",
    )
    amount_fy2_internal = fields.Float(
        string='FY2 (I)',
        compute='_compute_amount_fy',
    )
    amount_fy3_internal = fields.Float(
        string='FY3 (I)',
        compute='_compute_amount_fy',
    )
    amount_fy4_internal = fields.Float(
        string='FY4 (I)',
        compute='_compute_amount_fy',
    )
    amount_beyond_internal = fields.Float(
        string='FY5 and Beyond (I)',
        compute='_compute_amount_fy',
    )
    revenue_budget = fields.Float(
        string='Revenue Budget',
    )
    overall_revenue_plan = fields.Float(
        string='Overall Revenue Plan',
    )
    proposal_overall_budget = fields.Float(
        string='Proposal Overall Budget (External)',
    )
    overall_expense_budget = fields.Float(
        string='Overall Expense Budget (External)',
    )
    overall_expense_budget_internal = fields.Float(
        string='Overall Expense Budget (Internal)',
    )
    project_type_id = fields.Many2one(
        'project.type',
        string='Project Type',
    )
    project_kind = fields.Selection(
        [('research', 'Research'),
         ('non_research', 'Non Research'),
         ('management', 'Management Program/Cluster'),
         ('construction', 'Construction'), ],
        related='project_type_id.project_kind',
        string='Project Kind',
        store=True,
        readonly=True,
    )
    subprogram_id = fields.Many2one(
        'project.subprogram',
        string='Subprogram',
    )
    current_fy_release_only = fields.Boolean(
        string='Allow Current FY Release Only',
        default=True,
        help="By default only current FY is allowed to release.\n"
        "We are doing this as temp solution, in the future it might "
        "be configurable somewhere else."
    )
    active = fields.Boolean(
        compute='_compute_active',
        store=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        related='pm_employee_id.org_id',
        store=True,
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Cost Center',
        related='pm_employee_id.costcenter_id',
        store=True,
        readonly=True,
    )
    more_project_member_ids = fields.Many2many(
        'hr.employee',
        'project_hr_employee_rel',
        'project_id',
        'employee_id',
        string='More Project Member',
    )
    conversion_project = fields.Boolean(
        string='Conversion Project',
        default=False,
    )
    _sql_constraints = [
        ('code_unique', 'unique(code)',
         'Project Code must be unique!'),
    ]

    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for rec in self:
            rec.active = rec.state in ('draft', 'approve')
        return True

    @api.onchange('pm_employee_id')
    def _onchange_user_id(self):
        self.owner_disivion_id = self.pm_employee_id.section_id.division_id

    @api.onchange('analyst_employee_id')
    def _onchange_analyst_employee_id(self):
        self.analyst_section_id = self.analyst_employee_id.section_id

    @api.model
    def find_active_project_budget(self, fiscalyear_ids, program_ids):
        budgets = self.env['account.budget'].search([
            ('chart_view', '=', 'project_base'),
            ('fiscalyear_id', 'in', fiscalyear_ids),
            ('program_id', 'in', program_ids)])
        return budgets

    @api.multi
    def _compute_budget_count(self):
        for rec in self:
            # Show all budget control with same program and fiscalyear
            budgets = self.find_active_project_budget(
                rec.fiscalyear_ids.ids, [rec.program_id.id])
            rec.budget_count = len(budgets)

    @api.multi
    @api.depends('budget_plan_ids')
    def _compute_budget_to_sync_count(self):
        for rec in self:
            to_sync_fiscals = rec.budget_plan_ids.filtered(
                lambda l: not l.synced).mapped('fiscalyear_id')
            budgets = self.find_active_project_budget(
                to_sync_fiscals.ids, [rec.program_id.id])
            rec.budget_to_sync_count = len(budgets)

    @api.multi
    @api.depends('budget_plan_ids.fiscalyear_id')
    def _compute_fiscalyear_ids(self):
        for project in self:
            fiscalyear_ids = [x.fiscalyear_id.id
                              for x in project.budget_plan_ids]
            project.fiscalyear_ids = list(set(fiscalyear_ids))

    @api.multi
    def sync_project_plan_to_budget_line(self, fiscalyear_ids=False):
        """
        fiscalyear_ids specify which year to sync, otherwise, all sync.
        only sync if synced=False
        """
        for project in self:
            # Find phase with vaild sync history
            plan_syncs = not fiscalyear_ids and project.budget_plan_ids or \
                project.budget_plan_ids.filtered(
                    lambda l: l.fiscalyear_id.id in fiscalyear_ids)
            if not plan_syncs:
                continue
            for sync in plan_syncs:
                if not sync.sync_budget_line_id or sync.synced:
                    continue
                vals = {}
                vals.update({
                    'fiscalyear_id': sync.fiscalyear_id.id,
                    'budget_method': sync.budget_method,
                    'charge_type': sync.charge_type,
                    'income_section_id': sync.income_section_id.id,
                    'activity_group_id': sync.activity_group_id.id,
                    'released_amount': sync.released_amount})
                for i in range(1, 13):
                    vals['m' + str(i)] = sync['m' + str(i)]
                sync.sync_budget_line_id.write(vals)
                # Mark synced
                sync.write({'synced': True,
                            'last_sync': fields.Datetime.now()})
        return True

    @api.multi
    def action_sync_project_plan_to_budget_line(self):
        return self.sync_project_plan_to_budget_line(fiscalyear_ids=False)

    @api.multi
    def action_open_budget_control(self):
        self.ensure_one()
        # TODO: check for access?
        # self.env['res.invest.construction']._check_cooperate_access()
        action = self.env.ref('pabi_chartfield.'
                              'act_account_budget_view_project_base')
        result = action.read()[0]
        budgets = self.find_active_project_budget(self.fiscalyear_ids.ids,
                                                  [self.program_id.id])
        dom = [('id', 'in', budgets.ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    def action_open_to_sync_budget_control(self):
        self.ensure_one()
        # TODO: check for access?
        # self.env['res.invest.construction']._check_cooperate_access()
        action = self.env.ref('pabi_chartfield.'
                              'act_account_budget_view_project_base')
        result = action.read()[0]
        to_sync_fiscals = self.budget_plan_ids.filtered(
            lambda l: not l.synced).mapped('fiscalyear_id')
        budgets = self.find_active_project_budget(to_sync_fiscals.ids,
                                                  [self.program_id.id])
        dom = [('id', 'in', budgets.ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    @api.constrains('budget_plan_ids', 'budget_plan_expense_ids',
                    'budget_plan_revenue_ids')
    def _trigger_auto_sync(self):
        self.sync_budget_control()

    @api.multi
    def sync_budget_control(self):
        for project in self:
            to_sync_fiscals = project.budget_plan_ids.filtered(
                lambda l: not l.synced).mapped('fiscalyear_id')
            budgets = self.find_active_project_budget(to_sync_fiscals.ids,
                                                      [project.program_id.id])
            for budget in budgets:
                if budget.project_auto_sync:
                    budget.with_context(
                        project_id=project.id).sync_budget_my_project()
        return True

    @api.multi
    def _release_fiscal_budget(self, fiscalyear, released_amount):
        """ Distribute budget released to all AG of the same year
            by distribute to the first AG first,
            show warning if released amount > planned amout
        """
        # Not current year, no budget release allowed
        current_fy = self.env['account.fiscalyear'].find()
        release_external_budget = fiscalyear.control_ext_charge_only
        ignore_current_fy = self._context.get('ignore_current_fy_lock', False)
        for project in self.sudo():
            if project.current_fy_release_only and \
                    current_fy != fiscalyear.id and \
                    not ignore_current_fy:
                raise ValidationError(
                    _('Not allow to release budget for fiscalyear %s!\nOnly '
                      'current year budget is allowed.' % fiscalyear.name))
            budget_plans = project.budget_plan_ids.filtered(lambda l: l.fiscalyear_id == fiscalyear)
            budget_monitor = project.monitor_expense_ids.filtered(lambda l: l.fiscalyear_id == fiscalyear and l.budget_method=='expense' and l.charge_type=='external')
            budget_plans.write({'released_amount': 0.0})  # Set zero
            if release_external_budget:  # Only for external charge
                budget_plans = budget_plans.filtered(
                    lambda l: l.charge_type == 'external'
                    and l.budget_method == 'expense')
            if not budget_plans:
                raise ValidationError(
                    _('Not allow to release budget for project without plan!'))
            planned_amount = sum([x.planned_amount for x in budget_plans])
            consumed_amount = sum([x.amount_consumed for x in budget_monitor])
            if float_compare(released_amount, planned_amount, 2) == 1 and \
                    not ignore_current_fy:
                raise ValidationError(
                    _('Releasing budget (%s) > planned (%s)!' %
                      ('{:,.2f}'.format(released_amount),
                       '{:,.2f}'.format(planned_amount))))
            if float_compare(released_amount, consumed_amount, 2) == -1 and \
                    not ignore_current_fy:
                raise ValidationError(
                    _('Releasing budget (%s) < Consumed Amount (%s)!' %
                      ('{:,.2f}'.format(released_amount),
                       '{:,.2f}'.format(consumed_amount))))
            remaining = released_amount
            update_vals = []
            for budget_plan in budget_plans:
                # remaining > planned_amount in line
                if float_compare(remaining,
                                 budget_plan.planned_amount, 2) == 1:
                    # expense only
                    if not budget_plan.planned_amount \
                            and budget_plan.budget_method == 'expense':
                        update = {'released_amount': remaining}
                        update_vals.append((1, budget_plan.id, update))
                        break
                    update = {'released_amount': budget_plan.planned_amount}
                    # case : last line
                    if budget_plan.id == budget_plans[-1].id:
                        update = {'released_amount': remaining}
                    remaining -= budget_plan.planned_amount
                    update_vals.append((1, budget_plan.id, update))
                else:
                    update = {'released_amount': remaining}
                    remaining = 0.0
                    update_vals.append((1, budget_plan.id, update))
                    break
            if update_vals:
                project.write({'budget_plan_ids': update_vals})
        return True

    @api.multi
    def write(self, vals):
        res = super(ResProject, self).write(vals)
        # If project group is changes, resync everything
        self.refresh_budget_line(vals)
        # Auto create fiscal plan line (for ease of use of user)
        self.prepare_fiscal_plan_line(vals)
        return res

    @api.multi
    def refresh_budget_line(self, vals):
        if 'project_group_id' in vals:
            for proj in self:
                # Delete all existing budget lines from this project
                proj.budget_plan_ids.mapped('sync_budget_line_id').unlink()
                # Find new budgets for this project
                budgets = self.find_active_project_budget(
                    proj.fiscalyear_ids.ids, [proj.program_id.id])
                if budgets:
                    for budget in budgets:
                        budget.with_context(project_id=proj.id).\
                            sync_budget_my_project()

    @api.model
    def _prepare_fiscal_plan_lines(self, project, budget_method):
        proj_fiscals = project.budget_plan_ids.\
            filtered(lambda l: l.budget_method == budget_method).\
            mapped('fiscalyear_id')
        Fiscal = self.env['account.fiscalyear']
        proj_date_end = datetime.strptime(project.date_end, '%Y-%m-%d')
        proj_date_end = proj_date_end + relativedelta(years=1)
        date_end = proj_date_end.strftime('%Y-%m-%d')
        fiscals = Fiscal.search([('date_start', '<=', date_end),
                                 ('date_stop', '>=', project.date_start)])
        fiscals -= proj_fiscals
        plan_lines = []
        for fiscal in fiscals:
            # Add both expense and revenue
            plan_lines.append((0, 0, {'fiscalyear_id': fiscal.id,
                                      'budget_method': budget_method}))
        project.write({'budget_plan_ids': plan_lines})

    @api.multi
    def prepare_fiscal_plan_line(self, vals, force_run=False):
        if force_run or \
                ('date_start' in vals and vals.get('date_start')) or \
                ('date_end' in vals and vals.get('date_end')):
            for proj in self:
                self._prepare_fiscal_plan_lines(proj, 'expense')
                self._prepare_fiscal_plan_lines(proj, 'revenue')

    @api.multi
    def _compute_amount_fy(self):
        Fiscal = self.env['account.fiscalyear']
        plan_fiscalyear_id = self._context.get('plan_fiscalyear_id', False)
        if plan_fiscalyear_id:
            current_fy = Fiscal.browse(plan_fiscalyear_id)
        else:
            current_fy = Fiscal.browse(Fiscal.find())
        for rec in self:
            for charge_type in ['external', 'internal']:

                plans = rec.budget_plan_expense_ids.\
                    filtered(lambda l: l.charge_type == charge_type)

                # Find previous years plan line
                prev_plans = plans.filtered(
                    lambda l: l.fiscalyear_id.date_start <
                    current_fy.date_start)

                if charge_type == 'external':
                    rec.amount_before = \
                        sum(prev_plans.mapped('planned_amount'))
                else:  # internal
                    rec.amount_before_internal = \
                        sum(prev_plans.mapped('planned_amount'))

                future_plans = plans - prev_plans  # current and future
                future_plans = future_plans.sorted(
                    key=lambda l: l.fiscalyear_id.date_start)
                amount_beyond = 0.0
                amount_beyond_internal = 0.0
                years = len(future_plans)

                if charge_type == 'external':
                    for i in range(0, years):
                        # Convert current_fy to date
                        current_fy_datetime = \
                            fields.Date.from_string(current_fy.date_start)
                        # Create next year and convert_fy to string
                        future_fy = fields.Date.to_string(
                            current_fy_datetime + relativedelta(years=i))
                        amount_year = sum(future_plans.filtered(
                            lambda l: l.fiscalyear_id.date_start ==
                            future_fy).mapped('planned_amount'))
                        if i < 4:  # only fy1 - fy4
                            rec['amount_fy%s' % (i + 1)] = amount_year
                        else:
                            amount_beyond += amount_year
                    rec.amount_beyond = amount_beyond
                else:  # internal
                    for i in range(0, years):
                        # Convert current_fy to date
                        current_fy_datetime = \
                            fields.Date.from_string(current_fy.date_start)
                        # Create next year and convert_fy to string
                        future_fy = fields.Date.to_string(
                            current_fy_datetime + relativedelta(years=i))
                        amount_year = sum(future_plans.filtered(
                            lambda l: l.fiscalyear_id.date_start ==
                            future_fy).mapped('planned_amount'))
                        if i < 4:  # only fy1 - fy5
                            rec['amount_fy%s_internal' % (i + 1)] = amount_year
                        else:
                            amount_beyond_internal += amount_year
                    rec.amount_beyond_internal = amount_beyond_internal

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Find matched project manager's projects
        project_manager_emp_id = self._context.get('project_manager_emp_id',
                                                   False)
        if project_manager_emp_id:
            PM = self.env['res.project.member']
            projects = PM.search([('project_position', '=', 'manager'),
                                  ('employee_id', '=', project_manager_emp_id)
                                  ])
            args += [('id', 'in', projects._ids)]
        return super(ResProject, self).name_search(name=name,
                                                   args=args,
                                                   operator=operator,
                                                   limit=limit)


class ResProjectMember(models.Model):
    _name = 'res.project.member'
    _description = 'Project Member'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
        required=True,
        index=True,
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        index=True,
        required=True,
    )
    project_position = fields.Selection([
        ('manager', "Project Manager"),
        ('member', "Member"), ],
        string='Position',
        required=True,
    )
    percent_participate = fields.Float(
        string='Percent (%)',
        default=0.0,
        required=True,
    )
    report_check = fields.Boolean(
        string='Report',
        default=True,
    )

    @api.one
    @api.constrains('project_id', 'employee_id', 'project_position')
    def _check_unique_project_manager(self):
        self._cr.execute("""
            select coalesce(count(*))
            from res_project_member
            where project_position = 'manager'
            and project_id = %s
        """, (self.project_id.id,))
        count = self._cr.fetchone()[0]
        if count > 1:
            raise ValidationError(
                _('There are project with > 1 project manager'))


class ResProjectBudgetPlan(models.Model):
    _name = 'res.project.budget.plan'
    _description = 'Project Budget Lines and Released Amount'
    _order = 'fiscalyear_id, id'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        required=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        default='expense',
        required=True,
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
    )
    income_section_id = fields.Many2one(
        'res.section',
        string='Income Section',
        domain=[('internal_charge', '=', True)],
    )
    description = fields.Text(
        string='Description',
        size=1000,
    )
    m1 = fields.Float(
        string='Oct',
        default=0.0,
    )
    m2 = fields.Float(
        string='Nov',
        default=0.0,
    )
    m3 = fields.Float(
        string='Dec',
        default=0.0,
    )
    m4 = fields.Float(
        string='Jan',
        default=0.0,
    )
    m5 = fields.Float(
        string='Feb',
        default=0.0,
    )
    m6 = fields.Float(
        string='Mar',
        default=0.0,
    )
    m7 = fields.Float(
        string='Apr',
        default=0.0,
    )
    m8 = fields.Float(
        string='May',
        default=0.0,
    )
    m9 = fields.Float(
        string='Jun',
        default=0.0,
    )
    m10 = fields.Float(
        string='Jul',
        default=0.0,
    )
    m11 = fields.Float(
        string='Aug',
        default=0.0,
    )
    m12 = fields.Float(
        string='Sep',
        default=0.0,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        store=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        default=0.0,
        copy=False,
    )
    # Sync information
    sync_budget_line_id = fields.Many2one(
        'account.budget.line',
        string='Budget Line Ref',
        index=True,
        ondelete='set null',
        copy=False,
        help="This is of latest version of fiscalyear's budget control",
    )
    budget_id = fields.Many2one(
        'account.budget',
        related='sync_budget_line_id.budget_id',
        string='Budget Control',
        store=True,
        readonly=True,
    )
    last_sync = fields.Datetime(
        string='Last Sync',
        help="Latest syncing date/time",
    )
    synced = fields.Boolean(
        string='Synced',
        default=False,
        copy=False,
        help="Checked when it is synced. Unchecked when plan is updated"
        "then it will be synced again",
    )
    expense_synced = fields.Boolean(
        string='Synced',
        related='synced',
    )
    revenue_synced = fields.Boolean(
        string='Synced',
        related='synced',
    )

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                  rec.m5, rec.m6, rec.m7, rec.m8,
                                  rec.m9, rec.m10, rec.m11, rec.m12
                                  ])
            rec.planned_amount = planned_amount

    @api.multi
    def write(self, vals):
        changes = vals.keys()
        test_keys = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                     'm7', 'm8', 'm9', 'm10', 'm11', 'm12',
                     'fiscalyear_id', 'activity_group_id', 'released_amount',
                     'charge_type', 'budget_method', 'income_section_id']
        # If budget line table is changed at least 1 field, mark synced = False
        if len(set(changes).intersection(test_keys)) > 0:
            vals.update({'synced': False})  # Line updated
        if 'released_amount' in vals:
            for rec in self:
                if self._context.get('ignore_lock_release', False):
                    continue
                if rec.project_id.lock_release and \
                        vals['released_amount'] != rec.released_amount:
                    raise ValidationError(_('Budget released is locked!'))
        return super(ResProjectBudgetPlan, self).write(vals)

    @api.multi
    def unlink(self):
        """ As the line is deleted, also delete the related budget control """
        self.mapped('sync_budget_line_id').unlink()
        return super(ResProjectBudgetPlan, self).unlink()


class ResProjectBudgetSummary(models.Model):
    _name = 'res.project.budget.summary'
    _auto = False
    _rec_name = 'fiscalyear_id'
    _order = 'fiscalyear_id'
    _description = 'Fiscal Year summary of each phase amount'

    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='fiscalyear',
        readonly=True,
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        readonly=True,
    )
    allow_release = fields.Boolean(
        string='Allow Release',
        compute='_compute_allow_release',
    )

    @api.multi
    def _compute_allow_release(self):
        this_fy_id = self.env['account.fiscalyear'].find()
        for rec in self:
            if not rec.project_id.current_fy_release_only:
                rec.allow_release = True
            else:
                if rec.fiscalyear_id.id == this_fy_id:
                    rec.allow_release = True
                else:
                    rec.allow_release = False

    def init(self, cr):

        _sql = """
            select min(p.id) as id, project_id, fiscalyear_id, budget_method,
              sum(
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m1 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m2 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m3 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m4 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m5 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m6 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m7 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m8 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m9 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m10 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m11 end +
                case when control_ext_charge_only = true and
                charge_type = 'internal' then 0.0 else m12 end
            ) as planned_amount,
            sum(released_amount) as released_amount
            from res_project_budget_plan p
            join account_fiscalyear f on p.fiscalyear_id = f.id
            group by project_id, fiscalyear_id, budget_method
        """

        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" %
            (self._table, _sql,))


class ResProjectBudgetRelease(models.Model):
    _name = 'res.project.budget.release'
    _description = 'History of budget release (interface with myProject)'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        required=True,
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        required=True,
        index=True,
        ondelete='cascade',
    )
    dummy_project_id = fields.Many2one(
        related='project_id',
        help="Dummy project_id, used to calculate init amount release",
    )
    released_amount = fields.Float(
        string='Released Amount',
        default=0.0,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
        required=True,
    )
    write_date = fields.Datetime(
        readonly=True,
    )

    @api.onchange('fiscalyear_id', 'project_id')
    def _onchange_project_fiscal(self):
        BudgetSummary = self.env['res.project.budget.summary']
        project_id = \
            self._context.get('project_id', False) or self.project_id.id
        summary = BudgetSummary.search([
            ('project_id', '=', project_id),
            ('fiscalyear_id', '=', self.fiscalyear_id.id)])
        self.released_amount = summary and summary[0].released_amount or 0.0

    @api.model
    def create(self, vals):
        rec = super(ResProjectBudgetRelease, self).create(vals)
        carry_forward = self._context.get('button_carry_forward', False)
        carry_forward_async = \
            self._context.get('button_carry_forward_async_process', False)
        if 'released_amount' in vals and not carry_forward and \
                not carry_forward_async:
            rec.project_id._release_fiscal_budget(rec.fiscalyear_id,
                                                  rec.released_amount)
        return rec

    @api.multi
    def write(self, vals):
        result = super(ResProjectBudgetRelease, self).write(vals)
        if 'released_amount' in vals:
            for rec in self:
                rec.project_id._release_fiscal_budget(rec.fiscalyear_id,
                                                      rec.released_amount)
        return result

    @api.multi
    def dummy(self):
        """ This will by default, trigger the write() to release budget """
        return True


class MyProjectStatus(ResCommon, models.Model):
    _name = 'myproject.status'
    _description = 'myProject Status'

    res_project_state = fields.Selection(
        MY_PROJECT_STATES,
        string='Project State'
    )


class ProposalStatus(ResCommon, models.Model):
    _name = 'proposal.status'
    _description = 'Proposal Status'


class ProgramTarget(ResCommon, models.Model):
    _name = 'program.target'
    _description = 'Program Target'
