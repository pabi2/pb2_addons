# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp import tools
from openerp.tools import float_compare
from openerp.exceptions import ValidationError
from openerp.addons.pabi_base.models.res_investment_structure \
    import CONSTRUCTION_PHASE
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class ResInvestConstruction(LogCommon, models.Model):
    _name = 'res.invest.construction'
    _inherit = ['res.invest.construction', 'mail.thread']

    code = fields.Char(
        readonly=True,
        default='/',
        copy=False,
        track_visibility='onchange',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('unapprove', 'Un-Approved'),
         ('approve', 'Approved'),
         ('reject', 'Rejected'),
         ('delete', 'Deleted'),
         ('cancel', 'Cancelled'),
         ('close', 'Closed'),
         ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        default='draft',
        track_visibility='onchange',
    )
    month_duration = fields.Integer(
        string='Duration (months)',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        copy=False,
        track_visibility='onchange',
    )
    date_start = fields.Date(
        string='Start Date',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        copy=False,
        track_visibility='onchange',
    )
    date_end = fields.Date(
        string='End Date',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        copy=False,
        track_visibility='onchange',
    )
    pm_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    pm_section_id = fields.Many2one(
        'res.section',
        string='Project Manager Section',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Core Mission',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    amount_budget_plan = fields.Float(
        string='Planned Budget',
        compute='_compute_amount_budget_plan',
        readonly=True,
        track_visibility='onchange',
    )
    amount_budget = fields.Float(
        string='Approved Budget',
        default=0.0,
        readonly=True,
        states={'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        write=['pabi_base.group_cooperate_budget'],  # Only Corp can edit
        track_visibility='onchange',
    )
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
    amount_phase_approve = fields.Float(
        string='Approved Budget (Phases)',
        compute='_compute_amount_phase_approve',
        store=True,
    )
    operation_area = fields.Char(
        string='Operation Area',
        track_visibility='onchange',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
        track_visibility='onchange',
    )
    approval_info = fields.Text(
        string='Approval Info',
        track_visibility='onchange',
        size=1000,
    )
    project_readiness = fields.Text(
        string='Project Readiness',
        track_visibility='onchange',
        size=1000,
    )
    reason = fields.Text(
        string='Reason',
        track_visibility='onchange',
        size=1000,
    )
    expected_result = fields.Text(
        string='Expected Result',
        track_visibility='onchange',
        size=1000,
    )
    budget_plan_ids = fields.One2many(
        'res.invest.construction.budget.plan',
        'invest_construction_id',
        string='Budget Planning',
    )
    phase_ids = fields.One2many(
        domain=['|', ('active', '=', True), ('active', '=', False)],
    )
    legacy_ref = fields.Char(
        string='Legacy Ref.',
        readonly=False,
        size=500,
    )
    _sql_constraints = [
        ('number_uniq', 'unique(code)',
         'Constuction Project Code must be unique!'),
    ]

    @api.multi
    def _compute_amount_fy(self):
        Fiscal = self.env['account.fiscalyear']
        current_fy = Fiscal.browse(Fiscal.find())

        for rec in self:
            plans = rec.budget_plan_ids
            # Find current and previous years plan line
            prev_plans = plans.filtered(
                lambda l: l.fiscalyear_id.date_start <= current_fy.date_start)
            rec.amount_before = sum(prev_plans.mapped('amount_plan'))
            future_plans = plans - prev_plans  # Only future
            future_plans = future_plans.sorted(
                key=lambda l: l.fiscalyear_id.date_start)
            amount_beyond = 0.0
            years = len(future_plans)
            for i in range(0, years):
                if i < 4:  # only fy1 - fy4
                    rec['amount_fy%s' % (i + 1)] = future_plans[i].amount_plan
                else:
                    amount_beyond += future_plans[i].amount_plan
            rec.amount_beyond = amount_beyond

    @api.multi
    @api.constrains('budget_plan_ids')
    def _check_fiscalyear_unique(self):
        for rec in self:
            fiscalyear_ids = [x.fiscalyear_id.id for x in rec.budget_plan_ids]
            for x in fiscalyear_ids:
                if fiscalyear_ids.count(x) > 1:
                    raise ValidationError(_('Duplicate fiscalyear plan'))

    @api.model
    def _check_cooperate_access(self):
        if not self.env.user.has_group('pabi_base.group_cooperate_budget'):
            raise ValidationError(
                _('Only Cooperate Budget user is allowed!'))
        return True

    @api.multi
    @api.depends('phase_ids.amount_phase_approve')
    def _compute_amount_phase_approve(self):
        for rec in self:
            amount_total = sum([x.amount_phase_approve for x in rec.phase_ids])
            if amount_total and float_compare(amount_total,
                                              rec.amount_budget,
                                              precision_digits=2) != 0:
                raise ValidationError(
                    _("Sum of all phases approved budget <> "
                      "Project's approved budget"))
            rec.amount_phase_approve = amount_total

    @api.multi
    @api.constrains('date_expansion', 'date_start', 'date_end')
    def _check_date(self):
        for rec in self:
            # Date End must >= Date Start
            if rec.date_end and rec.date_start and \
                    rec.date_end < rec.date_start:
                raise ValidationError(
                    _('End Date must start after Start Date!'))
            # Expansion Date must >= End date
            if rec.date_expansion and rec.date_end and \
                    rec.date_expansion < rec.date_end:
                raise ValidationError(
                    _('Expansion Date must start after End Date!'))

    @api.multi
    @api.depends('budget_plan_ids.amount_plan')
    def _compute_amount_budget_plan(self):
        for rec in self:
            rec.amount_budget_plan = \
                sum([x.amount_plan for x in rec.budget_plan_ids])

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            fiscalyear_id = self.env['account.fiscalyear'].find()
            vals['code'] = self.env['ir.sequence'].\
                with_context(fiscalyear_id=fiscalyear_id).\
                next_by_code('invest.construction')
        return super(ResInvestConstruction, self).create(vals)

    @api.onchange('pm_employee_id')
    def _onchange_user_id(self):
        employee = self.pm_employee_id
        self.pm_section_id = employee.section_id
        self.costcenter_id = employee.section_id.costcenter_id
        self.org_id = employee.org_id

    @api.onchange('month_duration', 'date_start', 'date_end')
    def _onchange_date(self):
        if not self.month_duration or not self.date_start:
            self.date_end = False
        else:
            date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()
            date_end = date_start + relativedelta(months=self.month_duration)
            self.date_end = date_end.strftime('%Y-%m-%d')
        self._prepare_budget_plan_line(self.date_start, self.date_end)

    @api.model
    def _prepare_budget_plan_line(self, date_start, date_end):
        self.budget_plan_ids = False
        Fiscal = self.env['account.fiscalyear']
        Plan = self.env['res.invest.construction.budget.plan']
        if date_start and date_end:
            fiscal_start_id = Fiscal.find(date_start)
            fiscal_end_id = Fiscal.find(date_end)
            fiscal_start = Fiscal.browse(fiscal_start_id)
            fiscal_end = Fiscal.browse(fiscal_end_id)
            if not fiscal_start.name.isdigit():
                raise ValidationError(
                    _("Config: Fiscalyear name not represent a year integer!"))
            fiscal_year = int(fiscal_start.name)
            while fiscal_year <= int(fiscal_end.name):
                fiscal = Fiscal.search([('name', '=', str(fiscal_year))])
                if fiscal:
                    plan = Plan.new()
                    plan.fiscalyear_id = fiscal
                    plan.amount_plan = 0.0
                    self.budget_plan_ids += plan
                fiscal_year += 1
        return True

    @api.multi
    def action_create_phase(self):
        for rec in self:
            if rec.phase_ids:
                continue
            phases = []
            i = 1
            for phase in sorted(CONSTRUCTION_PHASE.items()):
                phases.append((0, 0, {'sequence': i,
                                      'phase': phase[0],
                                      'date_start': rec.date_start,
                                      'fund_ids': [(6, 0, rec.fund_ids.ids)],
                                      }))
                i += 1
            rec.write({'phase_ids': phases})

    # Statuses
    @api.multi
    def action_submit(self):
        for rec in self:
            if not rec.amount_budget_plan:
                raise ValidationError(
                    _('Cannot submit project without planned amount.'))
        self.with_context(button_click=True).write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        self._check_cooperate_access()
        self.action_create_phase()
        self.with_context(button_click=True).write({'state': 'approve'})

    @api.multi
    def action_unapprove(self):
        # Unapprove all phases, only those in Approved state
        for rec in self:
            rec.phase_ids.filtered(
                lambda l: l.state == 'approve').action_unapprove()
        self.with_context(button_click=True).write({'state': 'unapprove'})

    @api.multi
    def action_reject(self):
        self.with_context(button_click=True).write({'state': 'reject'})

    @api.multi
    def action_delete(self):
        self.with_context(button_click=True).write({'state': 'delete'})

    @api.multi
    def action_cancel(self):
        self.with_context(button_click=True).write({'state': 'cancel'})

    @api.multi
    def action_close(self):
        self.with_context(button_click=True).write({'state': 'close'})

    @api.multi
    def action_draft(self):
        self.with_context(button_click=True).write({'state': 'draft'})

    @api.multi
    def write(self, vals):
        # Only cooperate budget allowed to edit when state == 'submit'
        button_click = self._context.get('button_click', False)
        for rec in self:
            if not button_click and rec.state == 'submit':
                self._check_cooperate_access()
        return super(ResInvestConstruction, self).write(vals)


class RestInvestConstructionPhase(LogCommon, models.Model):
    _name = 'res.invest.construction.phase'
    _inherit = ['res.invest.construction.phase', 'mail.thread']

    name = fields.Char(
        required=False,
        track_visibility='onchange',
    )
    active = fields.Boolean(
        string='Active',
        compute='_compute_active',
        store=True,
        track_visibility='onchange',
        help="Phase is activated only when approved",
    )
    code = fields.Char(
        readonly=True,
        default='/',
        copy=False,
        track_visibility='onchange',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        related='invest_construction_id.org_id',
        store=True,
        track_visibility='onchange',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        related='invest_construction_id.costcenter_id',
        store=True,
        track_visibility='onchange',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('unapprove', 'Un-Approved'),
         ('approve', 'Approved'),
         ('reject', 'Rejected'),
         ('delete', 'Deleted'),
         ('cancel', 'Cancelled'),
         ('close', 'Closed'),
         ],
        string='Status',
        readonly=True,
        required=True,
        copy=False,
        default='draft',
        track_visibility='onchange',
    )
    amount_phase_approve = fields.Float(
        string='Approved Budget (Phase)',
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        track_visibility='onchange',
    )
    amount_phase_plan = fields.Float(
        string='Planned Budget (Phase)',
        compute='_compute_amount_phase_plan',
        readonly=True,
    )
    amount_phase_diff = fields.Float(
        string='Unplanned Budget (Phase)',
        compute='_compute_amount_phase_plan',
        readonly=True,
    )
    month_duration = fields.Integer(
        string='Duration (months)',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        track_visibility='onchange',
    )
    date_start = fields.Date(
        string='Start Date',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        track_visibility='onchange',
    )
    date_end = fields.Date(
        string='End Date',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        track_visibility='onchange',
    )
    date_expansion = fields.Date(
        string='Date Expansion',
        track_visibility='onchange',
    )
    contract_day_duration = fields.Integer(
        string='Contract Duration (days)',
        readonly=True,
        states={'approve': [('readonly', False)], },
        track_visibility='onchange',
    )
    contract_date_start = fields.Date(
        string='Contract Start Date',
        readonly=True,
        states={'approve': [('readonly', False)], },
        track_visibility='onchange',
    )
    contract_date_end = fields.Date(
        string='Contract End Date',
        readonly=True,
        states={'approve': [('readonly', False)], },
        track_visibility='onchange',
    )
    contract_ids = fields.Many2many(
        'purchase.contract',
        string='Contract Number',
        readonly=True,
        states={'approve': [('readonly', False)], },
        track_visibility='onchange',
    )
    phase_plan_ids = fields.One2many(
        'res.invest.construction.phase.plan',
        'invest_construction_phase_id',
        string='Budget Planning (Phase)',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        'construction_phase_fiscalyear_rel', 'phase_id', 'fiscalyear_id',
        string='Related Fiscal Years',
        compute='_compute_fiscalyear_ids',
        store=True,
        help="All related fiscal years for this phases",
        track_visibility='onchange',
    )
    budget_count = fields.Integer(
        string='Budget Control Count',
        compute='_compute_budget_count',
    )
    budget_to_sync_count = fields.Integer(
        string='Budget Need Sync Count',
        compute='_compute_budget_to_sync_count',
    )
    to_sync = fields.Boolean(
        string='To Sync',
        compute='_compute_budget_to_sync_count',
    )
    sync_ids = fields.One2many(
        'res.invest.construction.phase.sync',
        'phase_id',
        string='Sync History',
        copy=False,
    )
    summary_ids = fields.One2many(
        'invest.construction.phase.summary',
        'phase_id',
        string='Phase Summary',
        readonly=True,
    )
    fund_type_id = fields.Many2one(
        'project.fund.type',
        string='Fund Type',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'unapprove': [('readonly', False)]},
        track_visibility='onchange',
    )
    legacy_ref = fields.Char(
        string='Legacy Ref.',
        readonly=False,
        size=500,
    )
    _sql_constraints = [
        ('number_uniq', 'unique(code)',
         'Constuction Phase Code must be unique!'),
    ]

    @api.multi
    @api.constrains('phase_plan_ids')
    def _check_fiscalyear_unique(self):
        for rec in self:
            period_ids = [x.calendar_period_id.id for x in rec.phase_plan_ids]
            for x in period_ids:
                if period_ids.count(x) > 1:
                    raise ValidationError(
                        _('Duplicate period in budget plan!'))

    @api.multi
    @api.constrains('date_expansion', 'date_start', 'date_end')
    def _check_date(self):
        for rec in self:
            # Date End must >= Date Start
            if rec.date_end and rec.date_start and \
                    rec.date_end < rec.date_start:
                raise ValidationError(
                    _('End Date must start after Start Date!'))
            # Expansion Date must >= End date
            if rec.date_expansion and rec.date_end and \
                    rec.date_expansion < rec.date_end:
                raise ValidationError(
                    _('Expansion Date must start after End Date!'))
            # -- Check with Project -- #
            c = rec.invest_construction_id
            # Date Start must >= Project's Date start
            if rec.date_start and c.date_start and \
                    rec.date_start < c.date_start:
                raise ValidationError(
                    _('Start Date must start after Project Start Date!'))
            # Date End must <= Project's Date End/Expansion
            if rec.date_end and (c.date_expansion or c.date_end) and \
                    rec.date_end > (c.date_expansion or c.date_end):
                raise ValidationError(
                    _('End Date must end before Project End Date!'))
            # Date Expansion must <= Project's Date End/Expansion
            if rec.date_expansion and (c.date_expansion or c.date_end) and \
                    rec.date_expansion > (c.date_expansion or c.date_end):
                raise ValidationError(
                    _('Expansion Date must end before '
                      'Project Expansion Date!'))

    @api.model
    def _get_changed_plan_fiscalyear(self, vals):
        # For changes, find the related fiscalyear_ids and update the sync
        PhasePlan = self.env['res.invest.construction.phase.plan']
        # Update (1)
        changed_plans = filter(lambda x: x[0] == 1,
                               vals.get('phase_plan_ids'))
        plan_ids = map(lambda x: x[1], changed_plans)
        plans = PhasePlan.browse(plan_ids)
        year_ids = [x.fiscalyear_id.id for x in plans]
        # Create (0)
        changed_plans = filter(lambda x: x[0] == 0 and x[1] is False,
                               vals.get('phase_plan_ids'))
        year_ids += map(lambda x: x[2].get('fiscalyear_id'), changed_plans)
        return year_ids

    @api.multi
    def write(self, vals):
        if vals.get('phase_plan_ids', False):
            year_ids = self._get_changed_plan_fiscalyear(vals)
            for phase in self:
                phase.sync_ids.filtered(lambda l: l.fiscalyear_id.id
                                        in year_ids).write({'synced': False})
        # Track changes
        fk = 'invest_construction_id'
        track_fields = ['amount_phase_approve']
        self.env['pabi.utils'].track_lines(vals, fk, track_fields, self)
        # --
        return super(RestInvestConstructionPhase, self).write(vals)

    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for rec in self:
            rec.active = rec.state == 'approve'

    @api.model
    def find_active_construction_budget(self, fiscalyear_ids, org_ids):
        budgets = self.env['account.budget'].search([
            ('chart_view', '=', 'invest_construction'),
            ('fiscalyear_id', 'in', fiscalyear_ids),
            ('org_id', 'in', org_ids)])
        return budgets

    @api.multi
    def _compute_budget_count(self):
        for rec in self:
            # Show all budget control with the same org and same fiscalyear
            budgets = self.find_active_construction_budget(
                rec.fiscalyear_ids.ids, [rec.org_id.id])
            rec.budget_count = len(budgets)

    @api.multi
    @api.depends('sync_ids')
    def _compute_budget_to_sync_count(self):
        for rec in self:
            to_sync_fiscals = rec.sync_ids.filtered(
                lambda l: not l.synced).mapped('fiscalyear_id')
            budgets = self.find_active_construction_budget(
                to_sync_fiscals.ids, [rec.org_id.id])
            rec.budget_to_sync_count = len(budgets)
            rec.to_sync = len(budgets) > 0 and True or False

    @api.multi
    @api.depends('phase_plan_ids.amount_plan')
    def _compute_amount_phase_plan(self):
        for rec in self:
            rec.amount_phase_plan = \
                sum([x.amount_plan for x in rec.phase_plan_ids])
            rec.amount_phase_diff = \
                rec.amount_phase_approve - rec.amount_phase_plan

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            prefix = 'N/A-'
            if vals.get('invest_construction_id', False):
                project = self.env['res.invest.construction'].\
                    browse(vals.get('invest_construction_id'))
                prefix = str(project.code) + '-'
            vals['code'] = prefix + '{:02d}'.format(vals.get('sequence', 0))
        return super(RestInvestConstructionPhase, self).create(vals)

    @api.onchange('month_duration', 'date_start', 'date_end')
    def _onchange_date(self):
        if not self.month_duration or not self.date_start:
            self.date_end = False
        else:
            date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()
            date_end = date_start + relativedelta(months=self.month_duration)
            self.date_end = date_end.strftime('%Y-%m-%d')
        self._prepare_phase_plan_line(self.date_start, self.date_end)

    @api.onchange('contract_day_duration', 'contract_date_start',
                  'contract_date_end')
    def _onchange_contract_date(self):
        if not self.contract_day_duration or not self.contract_date_start:
            self.contract_date_end = False
        else:
            date_start = \
                datetime.strptime(self.contract_date_start, '%Y-%m-%d').date()
            date_end = \
                date_start + relativedelta(days=self.contract_day_duration)
            self.contract_date_end = date_end.strftime('%Y-%m-%d')

    @api.model
    def _prepare_phase_plan_line(self, date_start, date_end):
        self.phase_plan_ids = False
        Period = self.env['account.period']
        Plan = self.env['res.invest.construction.phase.plan']
        date = date_start
        if date and date_end:
            while date <= date_end:
                period = Period.find(date)
                plan = Plan.new()
                plan.calendar_period_id = period.id
                plan.amount_plan = 0.0
                self.phase_plan_ids += plan
                next_period = Period.next(period, 1)
                date = next_period.date_start
                if not next_period:
                    raise ValidationError(
                        _('No period configured for the target end date'))
        return True

    @api.multi
    @api.depends('phase_plan_ids.fiscalyear_id')
    def _compute_fiscalyear_ids(self):
        for phase in self:
            fiscalyear_ids = [x.fiscalyear_id.id
                              for x in phase.phase_plan_ids]
            phase.fiscalyear_ids = list(set(fiscalyear_ids))

    @api.model
    def _prepare_mo_dict(self, fiscalyear, prefix):
        """ {1: 'm10', ..., 12: 'm9'}, {'m1': False, ..., 'm12': False} """
        month = int(fiscalyear.date_start[5:7])
        mo_dict = {}
        for i in range(12):
            mo_dict.update({month: prefix + str(i + 1)})
            month += 1
            if month > 12:
                month = 1
        vals = dict([(v, False) for v in mo_dict.values()])
        return (mo_dict, vals)

    @api.multi
    def sync_phase_to_budget_line(self, fiscalyear_ids=False):
        """
        fiscalyear_ids specify which year to sync, otherwise, all sync.
        only sync if synced=False
        """
        for phase in self:
            # Find phase with vaild sync history (has been pulled before)
            phase_syncs = not fiscalyear_ids and phase.sync_ids or \
                phase.sync_ids.filtered(lambda l: l.fiscalyear_id.id
                                        in fiscalyear_ids)
            if not phase_syncs:
                continue
            for sync in phase_syncs:
                # No valid budate line reference, or already synced, ignore it
                # (need to pull from budget control first)
                if not sync.sync_budget_line_id or sync.synced:
                    continue
                # Prepare update dict
                fiscalyear = sync.fiscalyear_id
                mo_dict, vals = self._prepare_mo_dict(fiscalyear, 'm')
                # Update it
                for plan in phase.phase_plan_ids.filtered(
                        lambda l: l.fiscalyear_id.id == fiscalyear.id):
                    period = plan.calendar_period_id
                    month = int(period.date_start[5:7])
                    vals[mo_dict[month]] = plan.amount_plan
                sync.sync_budget_line_id.write(vals)
                # Mark synced
                sync.write({'synced': True,
                            'last_sync': fields.Datetime.now()})
        return True

    @api.multi
    def action_sync_phase_to_budget_line(self):
        return self.sync_phase_to_budget_line(fiscalyear_ids=False)  # do all

    @api.multi
    def _set_amount_plan_init(self):
        for phase in self:
            for plan in phase.phase_plan_ids:
                if not plan.init:
                    plan.amount_plan_init = plan.amount_plan
                    plan.init = True

    @api.multi
    def _check_amount_plan_approve(self):
        for phase in self:
            if float_compare(phase.amount_phase_plan,
                             phase.amount_phase_approve,
                             precision_digits=2) != 0:
                raise ValidationError(
                    _('Planned amount not equal to approved amount!'))

    @api.multi
    def _create_phase_sync(self):
        # Create phase sync of all fiscalyear_ids (if not exists)
        for phase in self:
            syncs = []
            exist_fiscal_ids = [x.fiscalyear_id.id for x in phase.sync_ids]
            for fiscalyear in phase.fiscalyear_ids:
                # Not already exists, create it.
                if fiscalyear.id not in exist_fiscal_ids:
                    sync = {'fiscalyear_id': fiscalyear.id,
                            'last_sync': False,
                            'synced': False, }
                    syncs.append((0, 0, sync))
            phase.write({'sync_ids': syncs})

    @api.multi
    def action_open_budget_control(self):
        self.ensure_one()
        self.env['res.invest.construction']._check_cooperate_access()
        action = self.env.ref('pabi_chartfield.'
                              'act_account_budget_view_invest_construction')
        result = action.read()[0]
        budgets = self.find_active_construction_budget(self.fiscalyear_ids.ids,
                                                       [self.org_id.id])
        dom = [('id', 'in', budgets.ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    def action_open_to_sync_budget_control(self):
        self.ensure_one()
        self.env['res.invest.construction']._check_cooperate_access()
        action = self.env.ref('pabi_chartfield.'
                              'act_account_budget_view_invest_construction')
        result = action.read()[0]
        to_sync_fiscals = self.sync_ids.filtered(
            lambda l: not l.synced).mapped('fiscalyear_id')
        budgets = self.find_active_construction_budget(to_sync_fiscals.ids,
                                                       [self.org_id.id])
        dom = [('id', 'in', budgets.ids)]
        result.update({'domain': dom})
        return result

    # Statuses
    @api.multi
    def action_submit(self):
        self._check_amount_plan_approve()
        self.write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        self.env['res.invest.construction']._check_cooperate_access()
        self._check_amount_plan_approve()
        self._set_amount_plan_init()
        self._create_phase_sync()
        self.write({'state': 'approve'})

    @api.multi
    def action_unapprove(self):
        self.write({'state': 'unapprove'})

    @api.multi
    def action_reject(self):
        self.write({'state': 'reject'})

    @api.multi
    def action_delete(self):
        self.write({'state': 'delete'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_close(self):
        self.write({'state': 'close'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    @api.constrains('sync_ids', 'state')
    def _trigger_auto_sync(self):
        for phase in self:
            to_sync_fiscals = phase.sync_ids.filtered(
                lambda l: not l.synced).mapped('fiscalyear_id')
            budgets = self.find_active_construction_budget(to_sync_fiscals.ids,
                                                           [phase.org_id.id])
            for budget in budgets:
                if budget.construction_auto_sync:
                    budget.with_context(
                        phase=phase.id).sync_budget_invest_construction()


class ResInvestConstructionBudgetPlan(models.Model):
    _name = 'res.invest.construction.budget.plan'
    _rec_name = 'fiscalyear_id'
    _description = 'Investment Construction Budget Plan'
    _order = 'fiscalyear_id'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Investment Construction',
        index=True,
        ondelete='cascade',
    )
    amount_plan = fields.Float(
        string='Amount',
        required=True,
    )

    @api.multi
    def write(self, vals):
        # Track changes
        fk = 'invest_construction_id'
        track_fields = ['amount_plan']
        self.env['pabi.utils'].track_lines(vals, fk, track_fields, self)
        # --
        return super(ResInvestConstructionBudgetPlan, self).write(vals)


class ResInvestConstructionPhasePlan(models.Model):
    _name = 'res.invest.construction.phase.plan'
    _rec_name = 'calendar_period_id'
    _description = 'Investment Construction Phase Plan'
    _order = 'calendar_period_id'

    id = fields.Integer(
        string='ID',
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
    )
    period_state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'), ],
        string='Period Status',
        related='calendar_period_id.state',
    )
    # past_period_le = fields.Boolean(
    #     string='Readonly',
    #     compute='_compute_past_period',
    #     help="These peirods are less or equal to Today.\n"
    #     "Used for making amount readonly",
    # )
    # past_period_lt = fields.Boolean(
    #     string='Readonly',
    #     compute='_compute_past_period',
    #     help="These peirods are less then Today.\n"
    #     "Used for calculate rolling amount.",
    # )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        related='calendar_period_id.fiscalyear_id',
        string='Fiscal Year',
        readonly=True,
        store=True,
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Investment Construction Phase',
        index=True,
        ondelete='cascade',
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Investment Construction',
        related='invest_construction_phase_id.invest_construction_id',
        store=True,
    )
    init = fields.Boolean(
        string='Intit?',
        default=False,
        help="This field mark that amount_plan_init already init",
    )
    amount_plan_init = fields.Float(
        string='Initial Plan',
        readonly=True,
    )
    amount_plan = fields.Float(
        string='Current Plan',
        required=True,
    )

    @api.multi
    @api.constrains('calendar_period_id')
    def _check_calendar_period_id(self):
        for rec in self:
            # Start date and end date of period must between Start and End
            date_start = rec.invest_construction_phase_id.date_start
            date_end = rec.invest_construction_phase_id.date_expansion or \
                rec.invest_construction_phase_id.date_end
            if rec.calendar_period_id.date_stop < date_start or \
                    rec.calendar_period_id.date_start > date_end:
                raise ValidationError(
                    _('Period must be within start and date!'))

    # This will help protect user from edit past date
    # @api.multi
    # def write(self, vals):
    #     if 'amount_plan' in vals:
    #         for rec in self:
    #             today = fields.Date.context_today(self)
    #             if rec.calendar_period_id.date_start < today:
    #                 raise ValidationError(
    #                     _('Changing past period amount is not allowed!'))
    #     return super(ResInvestConstructionPhasePlan, self).write(vals)

    @api.multi
    def write(self, vals):
        # Track changes
        fk = 'invest_construction_phase_id'
        track_fields = ['amount_plan_init', 'amount_plan']
        self.env['pabi.utils'].track_lines(vals, fk, track_fields, self)
        # --
        return super(ResInvestConstructionPhasePlan, self).write(vals)


class ResInvestConstructionPhaseSync(models.Model):
    _name = 'res.invest.construction.phase.sync'
    _description = 'Investment Construction Phase Sync History'
    _order = 'fiscalyear_id'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
    )
    phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Phase',
        index=True,
        ondelete='cascade',
    )
    sync_budget_line_id = fields.Many2one(
        'account.budget.line',
        string='Budget Line Ref',
        index=True,
        ondelete='cascade',
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
        help="Checked when it is synced. Unchecked when phase is updated"
        "then it will be synced again",
    )


class InvestConstructionPhaseSummary(models.Model):
    _name = 'invest.construction.phase.summary'
    _auto = False
    _rec_name = 'fiscalyear_id'
    _description = 'Fiscal Year summary of each phase amount'

    phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Construction Phase',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='fiscalyear',
        readonly=True,
    )
    amount_plan = fields.Float(
        string='Plan',
        readonly=True,
    )

    def init(self, cr):

        _sql = """
            select min(id) as id, invest_construction_phase_id as phase_id,
                    fiscalyear_id, sum(amount_plan) as amount_plan
            from res_invest_construction_phase_plan
            group by invest_construction_phase_id, fiscalyear_id
        """

        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" %
            (self._table, _sql,))
