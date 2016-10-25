# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, ChartField


class BudgetFiscalPolicyBreakdown(models.Model):
    _name = 'budget.fiscal.policy.breakdown'
    _description = 'Fiscal Year Budget Policy'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
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
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
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
        string='Validating User',
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
        string='Ref Budget Policy',
        readonly=True,
    )
    version = fields.Float(
        string='Version',
        default=1.0,
        readonly=True,
#         states={'draft': [('readonly', False)]},
    )
    latest_version = fields.Boolean(
        string='Current',
        readonly=True,
        default=True,
        # compute='_compute_latest_version',  TODO: determine version
        help="Indicate latest revision of the same plan.",
    )

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
    def button_confirm(self):
        self.ensure_one()
        sum_policy_amount = sum([l.policy_amount for l in self.line_ids])
        if self.policy_overall != sum_policy_amount:
            raise UserError(_('Overall policy amount is not full filled'))
        name = self.env['ir.sequence'].\
            next_by_code('fiscal.policy.breakdown.unit')
        self.write({
            'name': name,
            'state': 'confirm',
            'validating_user_id': self._uid,
            'date_confirm': fields.Date.context_today(self),
        })
        return True

    @api.multi
    def prepare_budget_control(self):
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
            budget.prev_planned_amount = budget.planned_amount


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
