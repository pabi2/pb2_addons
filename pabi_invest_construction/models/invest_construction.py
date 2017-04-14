# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError
from openerp.addons.pabi_base.models.res_investment_structure \
    import CONSTRUCTION_PHASE


class ResInvestConstruction(models.Model):
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
    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    date_end = fields.Date(
        string='End Date',
        required=False,
    )
    pm_employee_id = fields.Many2one(
        'hr.employee',
        string='Project Manager',
        required=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Project Manager Section',
        required=True,
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
    )
    amount_budget_plan = fields.Float(
        string='Planned Budget',
        compute='_compute_amount_budget_plan',
    )
    amount_budget_approve = fields.Float(
        string='Approved Budget',
        default=0.0,
    )
    month_duration = fields.Integer(
        string='Duration (months)',
    )
    operation_area = fields.Char(
        string='Operation Area',
    )
    date_expansion = fields.Date(
        string='Expansion Date',
    )
    approval_info = fields.Text(
        string='Approval info',
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
    _sql_constraints = [
        ('number_uniq', 'unique(code)',
         'Constuction Project Code must be unique!'),
    ]

    @api.multi
    @api.depends('budget_plan_ids.amount_plan')
    def _compute_amount_budget_plan(self):
        for rec in self:
            rec.amount_budget_plan = \
                sum([x.amount_plan for x in rec.budget_plan_ids])

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].\
                next_by_code('invest.construction')
        return super(ResInvestConstruction, self).create(vals)

    @api.onchange('pm_employee_id')
    def _onchange_user_id(self):
        employee = self.pm_employee_id
        self.section_id = employee.section_id

    @api.onchange('month_duration', 'date_start')
    def _onchange_date(self):
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
                phases.append((0, 0, {'sequence': i, 'phase': phase[0]}))
                i += 1
            rec.write({'phase_ids': phases})

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


class RestInvestConstructionPhase(models.Model):
    _inherit = 'res.invest.construction.phase'

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
        readonly=True,
        required=True,
        copy=False,
        default='draft',
    )
    amount_phase_approve = fields.Float(
        string='Approved Budget (Phase)',
        default=0.0,
    )
    amount_phase_plan = fields.Float(
        string='Planned Budget (Phase)',
        compute='_compute_amount_phase_plan',
    )
    amount_phase_diff = fields.Float(
        string='Unplanned Budget (Phase)',
        compute='_compute_amount_phase_plan',
    )
    month_duration = fields.Integer(
        string='Duration (months)',
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    date_end = fields.Date(
        string='End Date',
        required=False,
    )
    date_expansion = fields.Date(
        string='Date Expansion',
    )
    contract_day_duration = fields.Integer(
        string='Contract Duration (days)',
    )
    contract_date_start = fields.Date(
        string='Contract Start Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    contract_date_end = fields.Date(
        string='Contract End Date',
        required=False,
    )
    contract_number = fields.Char(
        string='Contract Number',
    )
    phase_plan_ids = fields.One2many(
        'res.invest.construction.phase.plan',
        'invest_construction_phase_id',
        string='Budget Planning (Phase)',
    )
    _sql_constraints = [
        ('number_uniq', 'unique(code)',
         'Constuction Phase Code must be unique!'),
    ]

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

    @api.onchange('month_duration', 'date_start')
    def _onchange_date(self):
        date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()
        date_end = date_start + relativedelta(months=self.month_duration)
        self.date_end = date_end.strftime('%Y-%m-%d')
        self._prepare_phase_plan_line(self.date_start, self.date_end)

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
        readonly=True,
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
         'unique(invest_construction_id, fiscalyar_id)',
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
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        related='calendar_period_id.period_id.fiscalyear_id',
        string='Fiscal Year',
        required=True,
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
