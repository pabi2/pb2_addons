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
    # PLAN
    amount_overall = fields.Float(
        string='Overall Amount',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    amount_project_base = fields.Float(
        string='Project Based',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    amount_unit_base = fields.Float(
        string='Unit Based',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    amount_personnel = fields.Float(
        string='Personnel',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    amount_invest_asset = fields.Float(
        string='Investment Asset',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    amount_invest_construction = fields.Float(
        string='Investment Construction',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    # POLICY
    policy_overall = fields.Float(
        string='Overall Amount',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    policy_project_base = fields.Float(
        string='Project Based',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    policy_unit_base = fields.Float(
        string='Unit Based',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    policy_personnel = fields.Float(
        string='Personnel',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    policy_invest_asset = fields.Float(
        string='Investment Asset',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
    )
    policy_invest_construction = fields.Float(
        string='Investment Construction',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_compute_all',
        store=True,
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
        domain=[('chart_view', '=', 'project_base')],
    )
    unit_base_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Unit Based Budget Policy',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'unit_base')],
    )

    @api.multi
    @api.depends('line_ids')
    def _compute_all(self):
        for rec in self:
            # PLAN
            rec.amount_project_base = sum(rec.project_base_ids.
                                          mapped('planned_amount'))
            rec.amount_unit_base = sum(rec.unit_base_ids.
                                       mapped('planned_amount'))
            # POLICY
            rec.policy_project_base = sum(rec.project_base_ids.
                                          mapped('policy_amount'))
            rec.policy_unit_base = sum(rec.unit_base_ids.
                                       mapped('policy_amount'))

            # Overall
            rec.amount_overall = sum([rec.amount_project_base,
                                      rec.amount_unit_base])
            rec.policy_overall = sum([rec.policy_project_base,
                                      rec.policy_unit_base])

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

    @api.multi
    def prepare_fiscal_budget_policy(self):
        self.ensure_one()
        self.line_ids.unlink()  # Delete all

        _states = ('submit', 'approve')

        # Projects
        _sql = """
            select tmpl.chart_view, tmpl.program_id, bpp.amount_budget_request
            from budget_plan_project bpp
            join budget_plan_template tmpl on tmpl.id = bpp.template_id
            where tmpl.fiscalyear_id = %s and tmpl.state in %s
        """
        self._cr.execute(_sql % (self.fiscalyear_id.id, _states))
        res = self._cr.dictfetchall()
        lines = []
        for r in res:
            vals = {'chart_view': r['chart_view'],
                    'program_id': r['program_id'],
                    'planned_amount': r['amount_budget_request']}
            lines.append((0, 0, vals))
        self.write({'project_base_ids': lines})

        # Org
        _sql = """
            select tmpl.chart_view, tmpl.org_id,
            sum(bpu.amount_budget_request) as amount_budget_request
            from budget_plan_unit bpu
            join budget_plan_template tmpl on tmpl.id = bpu.template_id
            where tmpl.fiscalyear_id = %s and tmpl.state in %s
            group by tmpl.chart_view, tmpl.org_id
        """
        self._cr.execute(_sql % (self.fiscalyear_id.id, _states))
        res = self._cr.dictfetchall()
        lines = []
        for r in res:
            vals = {'chart_view': r['chart_view'],
                    'org_id': r['org_id'],
                    'planned_amount': r['amount_budget_request']}
            lines.append((0, 0, vals))
        self.write({'unit_base_ids': lines})


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
