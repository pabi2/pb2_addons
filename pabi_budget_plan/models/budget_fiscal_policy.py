# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, CHART_VIEW_FIELD, ChartField


class BudgetFiscalPolicy(models.Model):
    _name = 'budget.fiscal.policy'
    _description = 'Fiscal Year Budget Policy'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    version = fields.Float(
        string='Version',
        defaul=0.1,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Non current version of document will be set inactive",
        readonly=True,
        states={'draft': [('readonly', False)]},
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
        default=fields.Date.today(),
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
        states={'draft': [('readonly', False)]},
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
    amount_overall = fields.Float(
        string='Overall Amount',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_project_base = fields.Float(
        string='Project Based',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_unit_base = fields.Float(
        string='Unit Based',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_personnel = fields.Float(
        string='Personnel',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_invest_asset = fields.Float(
        string='Investment Asset',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_invest_construction = fields.Float(
        string='Investment Construction',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    line_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Policy Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    project_base_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Project Based Budget Policy',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    unit_base_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Unit Based Budget Policy',
        readonly=True,
        states={'draft': [('readonly', False)]},
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
        for rec in self:
            for line in rec.line_ids:
                res = line.\
                    _get_chained_dimension(CHART_VIEW_FIELD[line.chart_view])
                line.write(res)
        self.write({
            'state': 'confirm',
            'validating_user_id': self._uid,
            'date_confirm': fields.Date.today(),
        })
        return True


class BudgetFiscalPolicyLine(ChartField, models.Model):
    _name = 'budget.fiscal.policy.line'
    _description = 'Fiscal year Budget Policy Detail'

    budget_policy_id = fields.Many2one(
        'budget.fiscal.policy',
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )
