# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, ChartField


class BudgetFiscalPolicy(models.Model):
    _name = 'budget.fiscal.policy'
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
        default="/",
        copy=False,
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
    planned_overall = fields.Float(
        string='Planned Overall',
        compute='_compute_all',
        store=True,
    )
    planned_project_base = fields.Float(
        string='Project Based',
        compute='_compute_all',
        store=True,
    )
    planned_unit_base = fields.Float(
        string='Unit Based',
        compute='_compute_all',
        store=True,
    )
    planned_personnel = fields.Float(
        string='Personnel',
        compute='_compute_all',
        store=True,
    )
    planned_invest_asset = fields.Float(
        string='Investment Asset',
        compute='_compute_all',
        store=True,
    )
    planned_invest_construction = fields.Float(
        string='Investment Construction',
        compute='_compute_all',
        store=True,
    )
    # POLICY
    policy_overall = fields.Float(
        string='Policy Overall',
        compute='_compute_all',
        store=True,
    )
    policy_project_base = fields.Float(
        string='Project Based',
        compute='_compute_all',
        store=True,
    )
    policy_unit_base = fields.Float(
        string='Unit Based',
        compute='_compute_all',
        store=True,
    )
    policy_personnel = fields.Float(
        string='Personnel',
        compute='_compute_all',
        store=True,
    )
    policy_invest_asset = fields.Float(
        string='Investment Asset',
        compute='_compute_all',
        store=True,
    )
    policy_invest_construction = fields.Float(
        string='Investment Construction',
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
    personnel_costcenter_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Personnel Budget Policy',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'personnel')],
    )
    invest_asset_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Investment Asset Budget Policy',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'invest_asset')],
    )
    invest_construction_ids = fields.One2many(
        'budget.fiscal.policy.line',
        'budget_policy_id',
        string='Investment Construction Budget Policy',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'invest_construction')],
    )
    # Smart buttons
    unit_breakdown_count = fields.Integer(
        string='Unit Based Breakdown Count',
        compute='_compute_breakdown_count',
    )
    invest_asset_breakdown_count = fields.Integer(
        string='Investment Asset Breakdown Count',
        compute='_compute_breakdown_count',
    )
    ref_policy_id = fields.Many2one(
        'budget.fiscal.policy',
        string="Policy Reference",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_get_company,
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=_get_currency,
        required=True,
    )

    @api.multi
    def action_open_breakdown(self):
        self.ensure_one()
        Breakdown = self.env['budget.fiscal.policy.breakdown']
        act = False
        domain = [('fiscalyear_id', '=', self.fiscalyear_id.id),
                  ('ref_budget_policy_id', '=', self.id)]
        if self._context.get('chart_view') == 'unit_base':
            act = 'pabi_budget_plan.action_unit_base_policy_breakdown_view'
            domain.append(('chart_view', '=', 'unit_base'))
        elif self._context.get('chart_view') == 'invest_asset':
            act = 'pabi_budget_plan.action_invest_asset_policy_breakdown_view'
            domain.append(('chart_view', '=', 'invest_asset'))
        Breakdown_ids = Breakdown.search(domain).ids
        action = self.env.ref(act)
        result = action.read()[0]
        result.update({'domain': [('id', 'in', Breakdown_ids)]})
        return result

    @api.multi
    def _compute_breakdown_count(self):
        Breakdown = self.env['budget.fiscal.policy.breakdown']
        for rec in self:
            domain = [('fiscalyear_id', '=', rec.fiscalyear_id.id),
                      ('ref_budget_policy_id', '=', rec.id)]
            rec.unit_breakdown_count = Breakdown.search_count(
                domain + [('chart_view', '=', 'unit_base')])
            rec.invest_asset_breakdown_count = Breakdown.search_count(
                domain + [('chart_view', '=', 'invest_asset')])

    @api.multi
    @api.depends('line_ids',
                 'line_ids.planned_amount',
                 'line_ids.policy_amount',
                 )
    def _compute_all(self):
        for rec in self:
            # PLAN
            rec.planned_project_base = sum(rec.project_base_ids.
                                           mapped('planned_amount'))
            rec.planned_unit_base = sum(rec.unit_base_ids.
                                        mapped('planned_amount'))
            rec.planned_personnel = sum(rec.personnel_costcenter_ids.
                                        mapped('planned_amount'))
            rec.planned_invest_asset = sum(rec.invest_asset_ids.
                                           mapped('planned_amount'))
            rec.planned_invest_construction = sum(rec.invest_construction_ids.
                                                  mapped('planned_amount'))
            # POLICY
            rec.policy_project_base = sum(rec.project_base_ids.
                                          mapped('policy_amount'))
            rec.policy_unit_base = sum(rec.unit_base_ids.
                                       mapped('policy_amount'))
            rec.policy_personnel = sum(rec.personnel_costcenter_ids.
                                       mapped('policy_amount'))
            rec.policy_invest_asset = sum(rec.invest_asset_ids.
                                          mapped('policy_amount'))
            rec.policy_invest_construction = sum(rec.invest_construction_ids.
                                                 mapped('policy_amount'))

            # Overall
            rec.planned_overall = sum([rec.planned_project_base,
                                      rec.planned_unit_base,
                                      rec.planned_personnel,
                                      rec.planned_invest_asset,
                                      rec.planned_invest_construction])
            rec.policy_overall = sum([rec.policy_project_base,
                                      rec.policy_unit_base,
                                      rec.policy_personnel,
                                      rec.policy_invest_asset,
                                      rec.policy_invest_construction])

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
        for policy in self:
            if not policy.line_ids:
                raise UserError(_('Can not confirm without lines!'))
            name = self.env['ir.sequence'].next_by_code('fiscal.budget.policy')
            policy.write({
                'name': name,
                'state': 'confirm',
                'validating_user_id': self._uid,
                'date_confirm': fields.Date.context_today(self),
            })
            policy.ref_policy_id.button_cancel()
        return True

    @api.multi
    def button_new_revision(self):
        self.ensure_one()
        budget_policy = self.copy()
        self.latest_version = False
        budget_policy.latest_version = True
        budget_policy.version = self.version + 1.0
        budget_policy.ref_policy_id = self
        # Copy Lines
        unit_base_ids = self.unit_base_ids.copy(default={'budget_policy_id': budget_policy.id})
        for unit_base in unit_base_ids:
            unit_base.budget_policy_id = budget_policy.id
        budget_policy.unit_base_ids = unit_base_ids
        #budget_policy.unit_base_ids.budget_policy_id = budget_policy.id
        budget_policy.project_base_ids = self.project_base_ids.copy()
        budget_policy.personnel_costcenter_ids =\
            self.personnel_costcenter_ids.copy()
        budget_policy.invest_asset_ids = self.invest_asset_ids.copy()
        budget_policy.invest_construction_ids =\
            self.invest_construction_ids.copy()
        budget_policy.name = '/'
        action = self.env.ref('pabi_budget_plan.'
                              'action_budget_fiscal_policy_view')
        result = action.read()[0]
        dom = [('id', '=', budget_policy.id)]
        result.update({'domain': dom})
        return result

    @api.multi
    def unlink(self):
        for policy in self:
            if policy.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('Cannot delete policies which are already confirmed.'))
        return super(BudgetFiscalPolicy, self).unlink()

    @api.multi
    def get_all_versions(self):
        self.ensure_one()
        fp_ids = []
        if self.ref_policy_id:
            fp = self.ref_policy_id
            while fp:
                fp_ids.append(fp.id)
                fp = fp.ref_policy_id
        fp = self
        while fp:
            rfp = self.search([('ref_policy_id', '=', fp.id)])
            if rfp:
                fp_ids.append(rfp.id)
            fp = rfp
        action = self.env.ref('pabi_budget_plan.'
                              'action_budget_fiscal_policy_view')
        result = action.read()[0]
        dom = [('id', 'in', fp_ids)]
        result.update({'domain': dom})
        return result

    # ======================== Prepare Budget Policy ==========================

    @api.multi
    def prepare_fiscal_budget_policy(self):
        self.ensure_one()
        self.line_ids.unlink()  # Delete all
        self._prepare_project_budget_policy()
        self._prepare_unit_budget_policy()
        self._prepare_invest_asset_budget_policy()

    @api.model
    def _prepare_project_budget_policy(self):
        self.ensure_one()
        # Projects
        _sql = """
            select tmpl.chart_view, tmpl.program_id, bpp.planned_overall
            from budget_plan_project bpp
            join budget_plan_template tmpl on tmpl.id = bpp.template_id
            where tmpl.fiscalyear_id = %s and tmpl.state = 'accept_corp'
        """
        self._cr.execute(_sql % (self.fiscalyear_id.id,))
        res = self._cr.dictfetchall()
        lines = []
        for r in res:
            vals = {'chart_view': r['chart_view'],
                    'program_id': r['program_id'],
                    'planned_amount': r['planned_overall']}
            lines.append((0, 0, vals))
        self.write({'project_base_ids': lines})

    @api.multi
    def _prepare_unit_budget_policy(self):
        self.ensure_one()
        # Unit Base, group by Org
        _sql = """
            select tmpl.chart_view, tmpl.org_id,
            sum(bpu.planned_overall) as planned_overall
            from budget_plan_unit bpu
            join budget_plan_template tmpl on tmpl.id = bpu.template_id
            where tmpl.fiscalyear_id = %s and tmpl.state = 'accept_corp'
            group by tmpl.chart_view, tmpl.org_id
        """
        self._cr.execute(_sql % (self.fiscalyear_id.id,))
        res = self._cr.dictfetchall()
        lines = []
        for r in res:
            vals = {'chart_view': r['chart_view'],
                    'org_id': r['org_id'],
                    'planned_amount': r['planned_overall']}
            lines.append((0, 0, vals))
        self.write({'unit_base_ids': lines})

    @api.model
    def _prepare_invest_asset_budget_policy(self):
        self.ensure_one()
        # Investment Asset, group by Org
        _sql = """
            select tmpl.chart_view,
            sum(bpia.planned_overall) as planned_overall
            from budget_plan_invest_asset bpia
            join budget_plan_template tmpl on tmpl.id = bpia.template_id
            where tmpl.fiscalyear_id = %s and tmpl.state = 'accept_corp'
            group by tmpl.chart_view
        """
        self._cr.execute(_sql % (self.fiscalyear_id.id,))
        res = self._cr.dictfetchall()
        lines = []
        for r in res:
            vals = {'chart_view': r['chart_view'],
                    'planned_amount': r['planned_overall']}
            lines.append((0, 0, vals))
        self.write({'invest_asset_ids': lines})

    # ========================================================================

    # ======================== Create Policy Breakdown =======================

    @api.multi
    def create_fiscal_budget_policy_breakdown(self):
        self.ensure_one()
        self.create_unit_budget_policy_breakdown()
        self.create_invest_asset_budget_policy_breakdown()

    @api.multi
    def create_unit_budget_policy_breakdown(self):
        self.ensure_one()
        Breakdown = self.env['budget.fiscal.policy.breakdown']
        BreakdownLine = self.env['budget.fiscal.policy.breakdown.line']
        domain = [('fiscalyear_id', '=', self.fiscalyear_id.id),
                      ('ref_budget_policy_id', '=', self.id)]
        Breakdown_search = Breakdown.search(
                domain + [('chart_view', '=', 'unit_base'),
                        ('state', '!=', 'cancel')
                ])
        if Breakdown_search:
            raise UserError(_('Breakdowns already created.'))
        for unit in self.unit_base_ids:
            ref_policy_id = unit.budget_policy_id.ref_policy_id
            ref_policy_breakdown = False
            if ref_policy_id:
                ref_policy_breakdown = Breakdown.search(
                    [('ref_budget_policy_id', '=', ref_policy_id.id),
                     ('org_id', '=', unit.org_id.id)])
                if ref_policy_breakdown:
                    ref_policy_breakdown = ref_policy_breakdown.id
            vals = {  # TODO: Sequence Numbering ???
                'name': unit.org_id.name,
                'chart_view': unit.chart_view,
                'org_id': unit.org_id.id,
                'planned_overall': unit.planned_amount,
                'policy_overall': unit.policy_amount,
                'fiscalyear_id': unit.budget_policy_id.fiscalyear_id.id,
                'ref_budget_policy_id': self.id,
                'version': unit.budget_policy_id.version,
                'ref_breakdown_id': ref_policy_breakdown,
            }
            breakdown = Breakdown.create(vals)
            plans = self.env['budget.plan.unit'].\
                search([('state', '=', 'accept_corp'),
                        ('fiscalyear_id', '=', breakdown.fiscalyear_id.id),
                        ('org_id', '=', breakdown.org_id.id)])
            for plan in plans:
                vals = {
                    'breakdown_id': breakdown.id,
                    'budget_plan_unit_id': plan.id,
                    'chart_view': plan.chart_view,
                    'section_id': plan.section_id.id,
                    'planned_amount': plan.planned_overall,
                    'policy_amount': 0.0,
                }
                BreakdownLine.create(vals)
            # Upon creation of breakdown, ensure data integrity
            sum_planned_amount = sum([l.planned_amount
                                      for l in breakdown.line_ids])
            if breakdown.planned_overall != sum_planned_amount:
                raise UserError(
                    _('For policy breakdown of Org: %s, \n'
                      'the overall planned amount is not equal to the '
                      'sum of all its sections') % (breakdown.org_id.name))

    @api.multi
    def create_invest_asset_budget_policy_breakdown(self):
        self.ensure_one()
        Breakdown = self.env['budget.fiscal.policy.breakdown']
        BreakdownLine = self.env['budget.fiscal.policy.breakdown.line']
        if self.invest_asset_ids:
            unit = self.invest_asset_ids[0]  # Always only 1 line in policy
            vals = {  # TODO: Sequence Numbering ???
                'name': 'NSTDA',
                'chart_view': unit.chart_view,
                'planned_overall': unit.planned_amount,
                'policy_overall': unit.policy_amount,
                'fiscalyear_id': unit.budget_policy_id.fiscalyear_id.id,
                'ref_budget_policy_id': self.id,
            }
            breakdown = Breakdown.create(vals)
            plans = self.env['budget.plan.invest.asset'].\
                search([('state', '=', 'approve'),
                        ('fiscalyear_id', '=', breakdown.fiscalyear_id.id)])
            for plan in plans:
                vals = {
                    'breakdown_id': breakdown.id,
                    'budget_plan_invest_asset_id': plan.id,
                    'chart_view': plan.chart_view,
                    'org_id': plan.org_id.id,
                    'planned_amount': plan.planned_overall,
                    'policy_amount': 0.0,
                }
                BreakdownLine.create(vals)
            # Upon creation of breakdown, ensure data integrity
            sum_planned_amount = sum([l.planned_amount
                                      for l in breakdown.line_ids])
            if breakdown.planned_overall != sum_planned_amount:
                raise UserError(
                    _('The overall planned amount is '
                      'not equal to the sum of all Orgs'))

    # ========================================================================


class BudgetFiscalPolicyLine(ChartField, models.Model):
    _name = 'budget.fiscal.policy.line'
    _description = 'Fiscal year Budget Policy Detail'

    budget_policy_id = fields.Many2one(
        'budget.fiscal.policy',
        ondelete='cascade',
        index=True,
    )
    budget_policy_version = fields.Float(
        related="budget_policy_id.version",
        string="Policy Version",
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
        compute='_compute_policy_amount',
        store=True,
    )
    policy_amount_v1 = fields.Float(
        string='Policy Amount Rev.1',
    )
    policy_amount_v2 = fields.Float(
        string='Policy Amount Rev.2',
    )
    policy_amount_v3 = fields.Float(
        string='Policy Amount Rev.3',
    )
    policy_amount_v4 = fields.Float(
        string='Policy Amount Rev.4',
    )
    policy_amount_v5 = fields.Float(
        string='Policy Amount Rev.5',
    )
    policy_amount_v6 = fields.Float(
        string='Policy Amount Rev.6',
    )
    policy_amount_v7 = fields.Float(
        string='Policy Amount Rev.7',
    )
    policy_amount_v8 = fields.Float(
        string='Policy Amount Rev.8',
    )
    policy_amount_v9 = fields.Float(
        string='Policy Amount Rev.9',
    )
    policy_amount_v10 = fields.Float(
        string='Policy Amount Rev.10',
    )
    policy_amount_v11 = fields.Float(
        string='Policy Amount Rev.11',
    )
    policy_amount_v12 = fields.Float(
        string='Policy Amount Rev.12',
    )

    @api.depends('policy_amount_v1',
                 'policy_amount_v2',
                 'policy_amount_v3',
                 'policy_amount_v4',
                 'policy_amount_v5',
                 'policy_amount_v6',
                 'policy_amount_v7',
                 'policy_amount_v8',
                 'policy_amount_v9',
                 'policy_amount_v10',
                 'policy_amount_v11',
                 'policy_amount_v12')
    def _compute_policy_amount(self):
        for line in self:
            version = line.budget_policy_version
            field_policy_amt = 'policy_amount_v' + str(int(version))
            line.policy_amount = sum(line.mapped(field_policy_amt))
