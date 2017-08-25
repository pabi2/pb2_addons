# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
        data = {
            'item_id': item.id,
            'invest_asset_id': item.invest_asset_id.id,
            'program_group_id': item.program_group_id.id,
            'm1': item.price_total,
        }
        return data

    @api.multi
    def convert_to_budget_plan(self):
        BudgetPlan = self.env['budget.plan.invest.asset']
        budget_plan_ids = []
        for asset_plan in self:
            # Geneate asset before create plan
            asset_plan.generate_invest_asset()
            # --
            budget_plan_vals = self._prepare_plan_header(asset_plan)
            line_vals = []
            for item in asset_plan.item_ids:
                if not item.select:
                    continue
                line_vals.append([0, 0, self._prepare_plan_line(item)])
            budget_plan_vals['plan_line_ids'] = line_vals
            budget_plan = BudgetPlan.create(budget_plan_vals)
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
    def action_view_invest_asset(self):
        self.ensure_one()
        invest_assets = self.item_ids.mapped('invest_asset_id')
        action = self.env.ref('pabi_base.action_res_invest_asset')
        dom = [('id', 'in', invest_assets.ids)]
        result = action.read()[0]
        result.update({'domain': dom})
        return result


class InvestAssetPlanItem(models.Model):
    _name = 'invest.asset.plan.item'
    _description = 'Investment Asset Plan Items'
    _rec_name = 'asset_name'

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
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
    )
    invest_asset_categ_id = fields.Many2one(
        'res.invest.asset.category',
        string='Investment Asset Category',
        required=True,
    )
    asset_common_name = fields.Char(
        string='Asset Common Name'
    )
    asset_name = fields.Char(
        string='Asset Name',
        required=True,
    )
    request_user_id = fields.Many2one(
        'hr.employee',
        string='Requester',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
        domain="[('org_id', '=', org_id)]",
    )
    division_id = fields.Many2one(
        'res.division',
        related='section_id.division_id',
        string='Division',
        readonly=True,
    )
    location = fields.Char(
        string='Asset Location',
    )
    quantity_plan = fields.Float(
        string='Quantity (Plan)',
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
    )
    price_unit = fields.Float(
        string='Unit Price',
        required=True,
    )
    price_subtotal = fields.Float(
        string='Price Subtotal',
        compute='_compute_price',
        store=True,
    )
    price_other = fields.Float(
        string='Other Expenses',
    )
    price_total = fields.Float(
        string='Price Total',
        compute='_compute_price',
        store=True,
    )
    reason_purchase = fields.Selection(
        [('new', 'New'),
         ('replace', 'Replacement'),
         ('extra', 'Extra')],
        string='Reason',
    )
    reason_purchase_text = fields.Text(
        string='Reason Desc.',
    )
    planned_utilization = fields.Char(
        string='Utilization (Hr/Yr)',
    )
    quotation_document = fields.Binary(
        string='Quotation',
    )
    specification_document = fields.Binary(
        string='Specification',
    )
    specification_summary = fields.Text(
        string='Summary of Specification',
    )

    # NOT SURE WHAT THIS SECTION IS ABOUT
    # total_commitment = fields.Float(
    #     string='Total Commitment',
    #     readonly=True,
    # )
    # pr_commitment = fields.Float(
    #     string='PR Commitment',
    #     readonly=True,
    # )
    # exp_commitment = fields.Float(
    #     string='EXP Commitment',
    #     readonly=True,
    # )
    # po_commitment = fields.Float(
    #     string='PO Commitment',
    #     readonly=True,
    # )
    # actual_amount = fields.Float(
    #     string='Actual',
    #     readonly=True,
    # )
    # total_commit_and_actual = fields.Float(
    #     string='Total Commitment + Actual',
    #     readonly=True,
    # )
    # budget_residual = fields.Float(
    #     string='Residual Budget',
    #     readonly=True,
    # )
    # --

    @api.multi
    @api.depends('price_unit', 'quantity', 'price_other')
    def _compute_price(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.quantity
            rec.price_total = rec.price_subtotal + rec.price_other

    @api.multi
    def _prepare_invest_asset(self):
        self.ensure_one()
        nstda_fund_id = self.env.ref('base.fund_nstda').id
        vals = {
            'name': self.asset_name,
            'invest_asset_categ_id': self.invest_asset_categ_id.id,
            'name_common': self.asset_common_name,
            'objective': self.reason_purchase_text,
            'owner_section_id': self.section_id.id,
            'org_id': self.org_id.id,
            'costcenter_id': self.section_id.costcenter_id.id,
            'fund_ids': [(4, nstda_fund_id)],
        }
        return vals

    @api.multi
    def convert_to_invest_asset(self):
        InvestAsset = self.env['res.invest.asset']
        invest_asset_ids = []
        for rec in self.filtered('select'):
            if rec.invest_asset_id:  # Exists, dont' create. Won't happen
                invest_asset_ids.append(rec.invest_asset_id.id)
                continue
            vals = rec._prepare_invest_asset()
            invest_asset = InvestAsset.create(vals)
            rec.invest_asset_id = invest_asset
            invest_asset_ids.append(invest_asset.id)
        return invest_asset_ids
