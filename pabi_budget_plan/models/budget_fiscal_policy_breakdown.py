# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, ChartField


class BudgetFiscalPolicyBreakdown(models.Model):
    _name = 'budget.fiscal.policy.breakdown'
    _inherit = ['mail.thread']
    _description = 'Fiscal Year Budget Policy'
    _order = 'create_date desc'

    @api.model
    def _get_company(self):
        company = self.env.user.company_id
        return company

    @api.model
    def _get_currency(self):
        company = self.env.user.company_id
        currency = company.currency_id
        return currency

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        default='/',
        copy=False,
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('budgeted', 'Budgeted'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        track_visibility='onchange',
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
        readonly=True,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Confirming User',
        readonly=True,
    )
    budgeting_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Budgeting User',
        readonly=True,
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_confirm = fields.Date(
        string='Confirmed Date',
        copy=False,
        readonly=True,
    )
    date_budget = fields.Date(
        string='Budgeting Date',
        copy=False,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    planned_overall = fields.Float(
        string='Planned Overall',
        required=True,
        readonly=True,
    )
    policy_overall = fields.Float(
        string='Policy Overall',
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        'budget.fiscal.policy.breakdown.line',
        'breakdown_id',
        string='Policy Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    unit_base_ids = fields.One2many(
        'budget.fiscal.policy.breakdown.line',
        'breakdown_id',
        string='Unit Based Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'unit_base')],
    )
    invest_asset_ids = fields.One2many(
        'budget.fiscal.policy.breakdown.line',
        'breakdown_id',
        string='Invest Asset Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'invest_asset')],
    )
    ref_budget_policy_id = fields.Many2one(
        'budget.fiscal.policy',
        string='Previous Budget Policy Breakdown',
        readonly=True,
    )
    version = fields.Float(
        string='Version',
        default=1.0,
        readonly=True,
    )
    latest_version = fields.Boolean(
        string='Current',
        readonly=True,
        default=True,
        # compute='_compute_latest_version',  TODO: determine version
        help="Indicate latest revision of the same plan.",
    )
    ref_breakdown_id = fields.Many2one(
        'budget.fiscal.policy.breakdown',
        string="Breakdown Reference",
        readonly=True,
        copy=False,
    )
    budget_control_count = fields.Integer(
        compute="_count_budget_control",
        string="Budget Controls",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_get_company,
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=_get_currency,
        readonly=True,
    )

    @api.depends()
    def _count_budget_control(self):
        for breakdown in self:
            counts = len(self.env['account.budget'].search(
                [('ref_breakdown_id', '=', breakdown.id)])._ids)
            breakdown.budget_control_count = counts

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def get_budget_controls(self):
        self.ensure_one()
        budget_controls =\
            self.env['account.budget'].search(
                [('ref_breakdown_id', '=', self.id)])
        act = 'account_budget_activity.act_account_budget_view'
        action = self.env.ref(act)
        result = action.read()[0]
        dom = [('id', 'in', budget_controls.ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    def button_confirm(self):
        self.ensure_one()
        sum_policy_amount = sum([l.policy_amount for l in self.line_ids])
        if self.policy_overall != sum_policy_amount:
            raise ValidationError(_('Overall policy amount is not full filled'))
        name = self.env['ir.sequence'].\
            next_by_code('fiscal.policy.breakdown.unit')
        self.write({
            'name': name,
            'state': 'confirm',
            'validating_user_id': self._uid,
            'date_confirm': fields.Date.context_today(self),
        })
        self.ref_breakdown_id.button_cancel()
        return True

    @api.multi
    def unlink(self):
        for policy in self:
            if policy.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('Cannot delete policy breakdown(s) \
                    which are already confirmed.'))
        return super(BudgetFiscalPolicyBreakdown, self).unlink()

    @api.multi
    def get_all_versions(self):
        self.ensure_one()
        breakdown_ids = []
        if self.ref_breakdown_id:
            breakdown = self.ref_breakdown_id
            while breakdown:
                breakdown_ids.append(breakdown.id)
                breakdown = breakdown.ref_breakdown_id
        breakdown = self
        while breakdown:
            ref_breakdown =\
                self.search([('ref_breakdown_id', '=', breakdown.id)])
            if ref_breakdown:
                breakdown_ids.append(ref_breakdown.id)
            breakdown = ref_breakdown
        act = False
        if self.chart_view == 'unit_base':
            act = 'pabi_budget_plan.action_unit_base_policy_breakdown_view'
        elif self.chart_view == 'invest_asset':
            act = 'pabi_budget_plan.action_invest_asset_policy_breakdown_view'
        action = self.env.ref(act)
        result = action.read()[0]
        dom = [('id', 'in', breakdown_ids)]
        result.update({'domain': dom})
        return result

    @api.multi
    def prepare_budget_control(self):
        # TODO: This seem to be the first time convert only.
        # Please check for the following minor revision also.
        self.ensure_one()
        data = {'unit_base': ('budget.plan.unit',
                              'budget_plan_unit_id'),
                'invest_asset': ('budget.plan.invest.asset',
                                 'budget_plan_invest_asset_id')}
        for line in self.line_ids:
            model = data[self.chart_view][0]
            active_id = line[data[self.chart_view][1]].id
            budget = self.env[model].convert_plan_to_budget_control(active_id)
            budget.policy_amount = line.policy_amount
            budget.version = line.breakdown_id.version
            # budget.prev_planned_amount = budget.planned_amount
            budget.prev_planned_amount = budget.budgeted_expense_external
            budget.ref_breakdown_id = line.breakdown_id.id
            old_breakdown = line.breakdown_id.ref_breakdown_id
            if old_breakdown:
                previous_budget =\
                    self.env['account.budget'].search(
                        [('section_id', '=', line.section_id.id),
                         ('chart_view', '=', self.chart_view),
                         ('active', '=', True),
                         ('ref_breakdown_id', '=', old_breakdown.id)],
                        order='version desc').ids
                if previous_budget:
                    budget.ref_budget_id = previous_budget[0]
        self.write({
            'state': 'budgeted',
            'date_budget': fields.Date.context_today(self),
            'budgeting_user_id': self._uid,
        })


class BudgetFiscalPolicyBreakdownLine(ChartField, models.Model):
    _name = 'budget.fiscal.policy.breakdown.line'
    _description = 'Fiscal year Budget Policy Breakdown Lines'

    breakdown_id = fields.Many2one(
        'budget.fiscal.policy.breakdown',
    )
    budget_plan_unit_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan - Unit Base',
        readonly=True,
    )
    budget_plan_invest_asset_id = fields.Many2one(
        'budget.plan.invest.asset',
        string='Budget Plan - Invest Asset',
        readonly=True,
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
        readonly=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=False,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=False,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )
