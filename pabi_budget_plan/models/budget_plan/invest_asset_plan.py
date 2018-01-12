# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_base.models.res_investment_structure import \
    InvestAssetCommon


class InvestAssetPlan(models.Model):
    _name = 'invest.asset.plan'
    _description = 'Investment Asset Planning'

    name = fields.Char(
        string='Name',
        required=True,
        default='/',
        readonly=False,
        states={'approve': [('readonly', True)],
                'done': [('readonly', True)]},
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        readonly=False,
        states={'approve': [('readonly', True)],
                'done': [('readonly', True)]},
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Validating User',
        readonly=False,
        states={'approve': [('readonly', True)],
                'done': [('readonly', True)]},
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
        readonly=False,
        states={'approve': [('readonly', True)],
                'done': [('readonly', True)]},
    )
    date_submit = fields.Date(
        string='Submitted Date',
        copy=False,
        readonly=True,
    )
    date_approve = fields.Date(
        string='Approved Date',
        copy=False,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=False,
        states={'approve': [('readonly', True)],
                'done': [('readonly', True)]},
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
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('cancel', 'Cancelled'),
         ('reject', 'Rejected'),
         ('approve', 'Approved'),
         ('done', 'Done')],
        string='Status',
        default='draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
        readonly=False,
        states={'approve': [('readonly', True)]},
    )
    verified_amount = fields.Float(
        string='Verified Amount',
        compute='_compute_verified',
    )
    item_ids = fields.One2many(
        'invest.asset.plan.item',
        'plan_id',
        string='Asset Items',
        readonly=False,
        states={'approve': [('readonly', True)],
                'done': [('readonly', True)]},

    )
    invest_asset_count = fields.Integer(
        string='Investment Asset Count',
        compute='_compute_invest_asset_count',
    )
    _sql_constraints = [
        ('uniq_plan', 'unique(org_id, fiscalyear_id)',
         'Duplicated budget plan for the same org is not allowed!'),
    ]

    @api.model
    def _get_doc_number(self, fiscalyear_id, model, res_id):
        _prefix = 'ASSET'
        fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
        res = self.env[model].browse(res_id)
        return '%s/%s/%s' % (_prefix, fiscal.code,
                             res.code or res.name_short or res.name)

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.org', vals['org_id'])
        vals.update({'name': name})
        return super(InvestAssetPlan, self).create(vals)

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        for rec in self:
            rec.date_from = rec.fiscalyear_id.date_start
            rec.date_to = rec.fiscalyear_id.date_stop

    @api.multi
    def button_submit(self):
        self.write({
            'state': 'submit',
            'date_submit': fields.Date.context_today(self),
        })
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return True

    @api.multi
    def button_approve(self):
        self.write({
            'state': 'approve',
            'validating_user_id': self._uid,
            'date_approve': fields.Date.context_today(self),
        })
        return True

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('org_id')._ids
        # Find orgs
        orgs = self.env['res.org'].search([('id', 'not in', _ids),
                                           ('special', '=', False)])
        plan_ids = []
        for org in orgs:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'org_id': org.id,
                                'user_id': False})
            plan_ids.append(plan.id)
        return plan_ids

    @api.multi
    def prepare_prev_fy_commitment(self):
        """ Prepre commitment amount from previous year from PO/EX """
        Fiscal = self.env['account.fiscalyear']
        Commit = self.env['invest.asset.plan.commit.view']
        self.mapped('item_ids').unlink()
        for plan in self:
            prev_fy = Fiscal.search(
                [('date_stop', '<', plan.fiscalyear_id.date_start)],
                order='date_stop desc', limit=1)
            if not prev_fy:
                return
            commits = Commit.search([
                ('org_id', '=', plan.org_id.id),
                ('fiscalyear_id', '=', prev_fy.id)])
            plan_lines = []
            for commit in commits:
                a = commit.invest_asset_id
                expenses = a.monitor_expense_ids
                all_actual = sum(expenses.mapped('amount_actual'))
                next_fy_ex = expenses.filtered(
                    lambda l: l.fiscalyear_id == plan.fiscalyear_id)
                next_fy_commit = sum(next_fy_ex.mapped('amount_pr_commit') +
                                     next_fy_ex.mapped('amount_po_commit') +
                                     next_fy_ex.mapped('amount_exp_commit'))
                vals = {
                    'select': True,
                    'priority': 0,
                    'invest_asset_id': a.id,
                    # Prev FY actual = all actual - current actal
                    'prev_fy_actual': all_actual - commit.actual,
                    'amount_plan': commit.released,
                    'pr_commitment': commit.pr_commit,
                    'exp_commitment': commit.exp_commit,
                    'po_commitment': commit.po_commit,
                    'total_commitment': commit.all_commit,
                    'actual_amount': commit.actual,
                    'budget_usage': commit.consumed,
                    'budget_remaining': commit.remain,
                    'budget_carry_forward': commit.carry_forward,
                    'next_fy_commitment': next_fy_commit,
                }
                vals.update(a._invest_asset_common_dict())
                plan_lines.append((0, 0, vals))
            plan.write({'item_ids': plan_lines})

    @api.one
    @api.depends('item_ids', 'item_ids.select')
    def _compute_verified(self):
        self.verified_amount = sum([x.price_total
                                   for x in self.item_ids if x.select])

    @api.model
    def _prepare_plan_header(self, asset_plan):
        data = {
            'name': asset_plan.name,
            'org_id': asset_plan.org_id.id,
            'creating_user_id': asset_plan.creating_user_id.id,
            'chart_view': 'invest_asset',
            'date': fields.Date.context_today(self),
            'fiscalyear_id': asset_plan.fiscalyear_id.id,
            'asset_plan_id': asset_plan.id,
        }
        return data

    @api.model
    def _prepare_plan_line(self, item):
        invest_asset = item.invest_asset_id
        data = {
            'invest_asset_id': invest_asset.id,
            'fund_id': invest_asset.fund_ids and invest_asset.fund_ids[0].id,
            # Commitment = current commitment + next year commitment
            'm0': item.all_commit + item.next_fy_commitment,
            # If first year of this asset, use amount_plan_total
            # for on going invest asset, use carry_forward
            'm1': (item.amount_plan == 0.0 and item.carry_forward == 0.0 and
                   item.amount_plan_total or item.carry_forward),
        }
        return data

    @api.multi
    def convert_to_budget_plan(self):
        BudgetPlan = self.env['budget.plan.invest.asset']
        budget_plan_ids = []
        for asset_plan in self:
            # Geneate asset before create plan
            asset_plan.generate_invest_asset()
            # Prepare Budget Plan
            budget_plan_vals = self._prepare_plan_header(asset_plan)
            line_vals = []
            for item in asset_plan.item_ids:
                if not item.select:
                    continue
                line_vals.append([0, 0, self._prepare_plan_line(item)])
            budget_plan_vals['plan_line_ids'] = line_vals
            budget_plan = BudgetPlan.create(budget_plan_vals)
            # --
            budget_plan_ids.append(budget_plan.id)
        self.write({'state': 'done'})
        return budget_plan_ids

    @api.multi
    def generate_invest_asset(self):
        self.ensure_one()
        invest_asset_ids = self.item_ids.convert_to_invest_asset()
        action = self.env.ref('pabi_base.action_res_invest_asset')
        result = action.read()[0]
        result.update({'domain': [('id', 'in', invest_asset_ids)]})
        return result

    @api.multi
    def _compute_invest_asset_count(self):
        for rec in self:
            rec.invest_asset_count = \
                len(rec.item_ids.mapped('invest_asset_id'))

    @api.multi
    def action_view_budget_plan(self):
        self.ensure_one()
        BudgetPlan = self.env['budget.plan.invest.asset']
        plan = BudgetPlan.search([('asset_plan_id', '=', self.id)])
        action = self.env.ref('pabi_budget_plan.'
                              'action_budget_plan_invest_asset_view')
        result = action.read()[0]
        view = self.env.ref('pabi_budget_plan.'
                            'view_budget_plan_invest_asset_form')
        result.update(
            {'res_id': plan[0].id,
             'view_id': False,
             'view_mode': 'form',
             'views': [(view.id, 'form')],
             'context': False, })

        return result

    @api.multi
    def action_view_invest_asset(self):
        self.ensure_one()
        invest_assets = self.item_ids.mapped('invest_asset_id')
        action = self.env.ref('pabi_base.action_res_invest_asset')
        dom = [('id', 'in', invest_assets.ids)]
        result = action.read()[0]
        result.update({'domain': dom})
        return result


class InvestAssetPlanItem(InvestAssetCommon, models.Model):
    _name = 'invest.asset.plan.item'
    _description = 'Investment Asset Plan Items'

    plan_id = fields.Many2one(
        'invest.asset.plan',
        string='Investment Asset Planning',
        readonly=True,
        index=True,
        ondelete='cascade',
    )
    select = fields.Boolean(
        string='Select',
        default=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='plan_id.org_id',
        string='Org',
        store=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        related='plan_id.fiscalyear_id',
        string='Fiscal Year',
        store=True,
    )
    priority = fields.Integer(
        string='Priority',
    )
    # Investment Asset Master Data
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Invest Asset',
        readonly=True,  # Not allow user to choose, it should come from history
    )
    # Additional Information to res.invest.asset
    name = fields.Char(
        string='Asset Name',
    )
    # All Prev FY Amount
    prev_fy_actual = fields.Float(
        string='Prev FY Actuals',
        readonly=True,
        help="All previous years actual combined",
    )
    # This FY Amount
    amount_plan = fields.Float(
        string='Current Budget',
        readonly=True,
        help="This FY Budget",
    )
    pr_commitment = fields.Float(
        string='Current PR Commit',
        readonly=True,
        help="This FY PR Commitment",
    )
    exp_commitment = fields.Float(
        string='Current EXP Commit',
        readonly=True,
        help="This FY EXP Commitment",
    )
    po_commitment = fields.Float(
        string='Current PO Commit',
        readonly=True,
        help="This FY PO Commitment",
    )
    total_commitment = fields.Float(
        string='Current Total Commit',
        readonly=True,
        help="This FY Total Commitment",
    )
    actual_amount = fields.Float(
        string='Current Actual',
        readonly=True,
        help="This FY actual amount",
    )
    budget_usage = fields.Float(
        string='Current Budget Usage',
        help="This FY Commitments + Actuals"
    )
    budget_remaining = fields.Float(
        string='Current Remaining Budget',
        help="This FY Budget Remaining"
    )
    budget_carry_forward = fields.Float(
        string='Budget Carry Forward',
        help="This FY Budget Remaining"
    )
    next_fy_commitment = fields.Float(
        string='Next FY Commitment',
        readonly=True,
        help="To be carried to upcoming year plan",
    )

    @api.multi
    def edit_asset_item(self):
        self.ensure_one()
        action = self.env.ref('pabi_budget_plan.'
                              'act_invest_asset_plan_item_view')
        result = action.read()[0]
        view = self.env.ref('pabi_budget_plan.'
                            'view_invest_asset_plan_item_form')
        result.update(
            {'res_id': self.id,
             'view_id': False,
             'view_mode': 'form',
             'views': [(view.id, 'form')],
             'context': False, })
        return result

    @api.multi
    @api.depends('price_unit', 'quantity', 'price_other')
    def _compute_price(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.quantity
            rec.price_total = rec.price_subtotal + rec.price_other

    @api.multi
    def convert_to_invest_asset(self):
        """ Create if not exists, update if already Exists
        Use data in invest asset item to overwrite the existing data """
        InvestAsset = self.env['res.invest.asset']
        invest_asset_ids = []
        for rec in self.filtered('select'):
            if rec.invest_asset_id:  # Exists, update data
                vals = rec._invest_asset_common_dict()
                rec.invest_asset_id.write(vals)
                invest_asset_ids.append(rec.invest_asset_id.id)
            else:
                vals = rec._invest_asset_common_dict()
                invest_asset = InvestAsset.create(vals)
                rec.invest_asset_id = invest_asset
                invest_asset_ids.append(invest_asset.id)
        return invest_asset_ids


class InvestAssetPlanCommitView(models.Model):
    _name = 'invest.asset.plan.commit.view'
    _auto = False
    _description = 'FY budget commitment for asset plan'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Invest Asset',
        readonly=True,
    )
    released = fields.Float(
        string='Released',
        readonly=True,
    )
    so_commit = fields.Float(
        string='SO Commit',
        readonly=True,
    )
    pr_commit = fields.Float(
        string='PR Commit',
        readonly=True,
    )
    po_commit = fields.Float(
        string='PO Commit',
        readonly=True,
    )
    exp_commit = fields.Float(
        string='EX Commit',
        readonly=True,
    )
    all_commit = fields.Float(
        string='All Commit',
        readonly=True,
    )
    actual = fields.Float(
        string='Actual',
        readonly=True,
    )
    consumed = fields.Float(
        string='Consumed',
        readonly=True,
    )
    remain = fields.Float(
        string='Ramining',
        readonly=True,
    )
    carry_forward = fields.Float(
        string='Carry Forward',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""create or replace view %s as (
            select max(id) id, invest_asset_id, fiscalyear_id, org_id,
                sum(released_amount) as released,
                -sum(amount_so_commit) so_commit,
                -sum(amount_pr_commit) pr_commit,
                -sum(amount_po_commit) po_commit,
                -sum(amount_exp_commit) exp_commit,
                -sum(amount_so_commit + amount_pr_commit +
                     amount_po_commit + amount_exp_commit) all_commit,
                -sum(amount_actual) actual,
                -sum(amount_consumed) consumed,
                sum(amount_balance) remain,
                sum(released_amount + amount_actual) carry_forward
            from budget_monitor_report
            where chart_view = 'invest_asset'
            group by invest_asset_id, fiscalyear_id, org_id
        )""" % self._table)
