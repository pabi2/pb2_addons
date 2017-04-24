# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError, ValidationError
from openerp.addons.pabi_base.models.res_investment_structure \
    import CONSTRUCTION_PHASE
from openerp.addons.document_status_history.models.document_history import \
    LogCommon


class ResInvestConstruction(LogCommon, models.Model):
    _inherit = 'res.invest.construction'

    code = fields.Char(
        readonly=True,
        default='/',
        copy=False,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
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
    )
    month_duration = fields.Integer(
        string='Duration (months)',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    date_end = fields.Date(
        string='End Date',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    pm_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    section_id = fields.Many2one(
        'res.section',
        string='Project Manager Section',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    org_id = fields.Many2one(
        'res.org',
        string='Project Manager Org',
        related='section_id.org_id',
        store=True,
        readonly=True,
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Core Mission',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    amount_budget_plan = fields.Float(
        string='Planned Budget',
        compute='_compute_amount_budget_plan',
        readonly=True,
    )
    amount_budget_approve = fields.Float(
        string='Approved Budget',
        default=0.0,
        readonly=True,
        states={'submit': [('readonly', False)]},
        write=['pabi_base.group_cooperate_budget'],  # Only Corp can edit
    )
    amount_phase_approve = fields.Float(
        string='Approved Budget (Phases)',
        compute='_compute_amount_phase_approve',
        store=True,
    )
    operation_area = fields.Char(
        string='Operation Area',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
    )
    approval_info = fields.Text(
        string='Approval Info',
    )
    project_readiness = fields.Text(
        string='Project Readiness',
    )
    reason = fields.Text(
        string='Reason',
    )
    expected_result = fields.Text(
        string='Expected Result',
    )
    budget_plan_ids = fields.One2many(
        'res.invest.construction.budget.plan',
        'invest_construction_id',
        string='Budget Planning',
    )
    phase_ids = fields.One2many(
        domain=['|', ('active', '=', True), ('active', '=', False)],
    )
    _sql_constraints = [
        ('number_uniq', 'unique(code)',
         'Constuction Project Code must be unique!'),
    ]

    @api.multi
    @api.depends('phase_ids.amount_phase_approve')
    def _compute_amount_phase_approve(self):
        for rec in self:
            amount_total = sum([x.amount_phase_approve for x in rec.phase_ids])
            if amount_total and amount_total != rec.amount_budget_approve:
                raise ValidationError(
                    _('Phases Approved Amount != Project Approved Amount'))
            rec.amount_phase_approve = amount_total

    @api.multi
    @api.constrains('date_expansion', 'date_start', 'date_end')
    def _check_date(self):
        for rec in self:
            # Date End must >= Date Start
            if rec.date_end and rec.date_start and \
                    rec.date_end < rec.date_start:
                raise ValidationError(
                    _('End Date must start after than Start Date!'))
            # Expansion Date must >= End date
            if rec.date_expansion and rec.date_end and \
                    rec.date_expansion < rec.date_end:
                raise ValidationError(
                    _('Expansion Date must start after than End Date!'))

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
        self.section_id = employee.section_id

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
            print rec.phase_ids
            if rec.phase_ids:
                continue
            phases = []
            i = 1
            for phase in sorted(CONSTRUCTION_PHASE.items()):
                phases.append((0, 0, {'sequence': i, 'phase': phase[0]}))
                i += 1
            rec.write({'phase_ids': phases})

    # Statuses
    @api.multi
    def action_submit(self):
        self.write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        self.action_create_phase()
        self.write({'state': 'approve'})

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


class RestInvestConstructionPhase(LogCommon, models.Model):
    _inherit = 'res.invest.construction.phase'

    active = fields.Boolean(
        string='Active',
        compute='_compute_active',
        store=True,
        help="Phase is activated only when approved",
    )
    code = fields.Char(
        readonly=True,
        default='/',
        copy=False,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        related='invest_construction_id.org_id',
        store=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
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
    )
    amount_phase_approve = fields.Float(
        string='Approved Budget (Phase)',
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
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
                'submit': [('readonly', False)]},
    )
    date_start = fields.Date(
        string='Start Date',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    date_end = fields.Date(
        string='End Date',
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
    )
    date_expansion = fields.Date(
        string='Date Expansion',
    )
    contract_day_duration = fields.Integer(
        string='Contract Duration (days)',
        readonly=True,
        states={'approve': [('readonly', False)], },
    )
    contract_date_start = fields.Date(
        string='Contract Start Date',
        readonly=True,
        states={'approve': [('readonly', False)], },
    )
    contract_date_end = fields.Date(
        string='Contract End Date',
        readonly=True,
        states={'approve': [('readonly', False)], },
    )
    contract_ids = fields.Many2many(
        'purchase.contract',
        string='Contract Number',
        readonly=True,
        states={'approve': [('readonly', False)], },
    )
    phase_plan_ids = fields.One2many(
        'res.invest.construction.phase.plan',
        'invest_construction_phase_id',
        string='Budget Planning (Phase)',
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        string='Related Fiscal Years',
        compute='_compute_fiscalyear_ids',
        help="All related fiscal years for this phases"
    )
    to_sync = fields.Boolean(
        string='To Sync',
        compute='_compute_to_sync',
        store=True,
        help="Some changes left to be synced"
    )
    sync_ids = fields.One2many(
        'res.invest.construction.phase.sync',
        'phase_id',
        string='Sync History',
        copy=False,
    )
    _sql_constraints = [
        ('number_uniq', 'unique(code)',
         'Constuction Phase Code must be unique!'),
    ]

    @api.multi
    @api.constrains('date_expansion', 'date_start', 'date_end')
    def _check_date(self):
        for rec in self:
            # Date End must >= Date Start
            if rec.date_end and rec.date_start and \
                    rec.date_end < rec.date_start:
                raise ValidationError(
                    _('End Date must start after than Start Date!'))
            # Expansion Date must >= End date
            if rec.date_expansion and rec.date_end and \
                    rec.date_expansion < rec.date_end:
                raise ValidationError(
                    _('Expansion Date must start after than End Date!'))
            # -- Check with Project -- #
            c = rec.invest_construction_id
            # Date Start must >= Project's Date start
            if rec.date_start and c.date_start and \
                    rec.date_start < c.date_start:
                raise ValidationError(
                    _('Start Date must start after than Project Start Date!'))
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
        return super(RestInvestConstructionPhase, self).write(vals)

    @api.multi
    @api.depends('state')
    def _compute_active(self):
        for rec in self:
            rec.active = rec.state == 'approve'

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
                    raise UserError(
                        _('No period configured for the target end date'))
        return True

    @api.multi
    @api.depends('phase_plan_ids.fiscalyear_id')
    def _compute_fiscalyear_ids(self):
        for phase in self:
            fiscalyear_ids = [x.fiscalyear_id.id
                              for x in phase.phase_plan_ids]
            phase.fiscalyear_ids = list(set(fiscalyear_ids))

    @api.multi
    @api.depends('sync_ids.synced')
    def _compute_to_sync(self):
        for phase in self:
            fiscalyear_ids = [x.fiscalyear_id.id
                              for x in phase.phase_plan_ids]
            phase.fiscalyear_ids = list(set(fiscalyear_ids))
            to_syncs = phase.sync_ids.filtered(lambda l: l.synced is False)
            phase.to_sync = len(to_syncs) > 0 and True or False

    @api.model
    def _prepare_mo_dict(self, fiscalyear):
        month = int(fiscalyear.date_start[5:7])
        mo_dict = {}
        for i in range(12):
            mo_dict.update({month: 'm' + str(i + 1)})
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
            print fiscalyear_ids
            print phase.sync_ids
            # Find phase with vaild sync history (has been pulled before)
            phase_syncs = not fiscalyear_ids and phase.sync_ids or \
                phase.sync_ids.filtered(lambda l: l.fiscalyear_id.id
                                        in fiscalyear_ids)
            print phase_syncs
            if not phase_syncs:
                continue
            for sync in phase_syncs:
                print sync
                # No valid budate line reference, or already synced, ignore it
                # (need to pull from budget control first)
                if not sync.sync_budget_line_id or sync.synced:
                    continue
                # Prepare update dict
                fiscalyear = sync.fiscalyear_id
                mo_dict, vals = self._prepare_mo_dict(fiscalyear)
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

    # Statuses
    @api.multi
    def action_submit(self):
        self.write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})

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


class ResInvestConstructionBudgetPlan(models.Model):
    _name = 'res.invest.construction.budget.plan'
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
    _sql_constraints = [
        ('construction_plan_uniq',
         'unique(invest_construction_id, fiscalyear_id)',
         'Fiscal year must be unique for a construction project!'),
    ]


class ResInvestConstructionPhasePlan(models.Model):
    _name = 'res.invest.construction.phase.plan'
    _description = 'Investment Construction Phase Plan'
    _order = 'calendar_period_id'

    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
    )
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
    amount_plan = fields.Float(
        string='Amount',
        required=True,
    )
    _sql_constraints = [
        ('construction_phase_plan_uniq',
         'unique(invest_construction_phase_id, calendar_period_id)',
         'Period must be unique for a construction phase!'),
    ]

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
        ondelete='set null',
    )
    budget_id = fields.Many2one(
        'account.budget',
        related='sync_budget_line_id.budget_id',
        string='Budget Control',
        readonly=True,
    )
    last_sync = fields.Datetime(
        string='Last Sync',
        help="Latest syncing date/time",
    )
    synced = fields.Boolean(
        string='Synced',
        default=False,
        help="Checked when it is synced. Unchecked when phase is updated"
        "then it will be synced again",
    )
