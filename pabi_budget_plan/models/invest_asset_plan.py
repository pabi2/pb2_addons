# -*- coding: utf-8 -*-
from openerp import models, fields, api


class InvestAssetPlan(models.Model):
    _name = 'invest.asset.plan'
    _description = 'Investment Asset Planning'

    name = fields.Char(
        string='Name',
        required=True,
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Validating User',
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
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
         ('approve', 'Approved')],
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
    )
    verified_amount = fields.Float(
        string='Verified Amount',
        compute='_compute_verified',
    )
    item_ids = fields.One2many(
        'invest.asset.plan.item',
        'plan_id',
        string='Asset Items'
    )

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
        print asset_plan.fiscalyear_id.id
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
    def _prepare_plan_line(self, item, budget_plan):
        data = {
            'plan_id': budget_plan.id,
            'org_id': item.org_id.id,
            'section_id': item.section_id.id,
            'program_group_id': item.program_group_id.id,
            'm1': item.price_total,
            'item_id': item.id,
        }
        return data

    @api.model
    def convert_to_budget_plan(self, active_ids):
        BudgetPlan = self.env['budget.plan.invest.asset']
        BudgetPlanLine = self.env['budget.plan.invest.asset.line']
        for asset_plan in self.browse(active_ids):
            head = self._prepare_plan_header(asset_plan)
            budget_plan = BudgetPlan.create(head)
            for item in asset_plan.item_ids:
                if not item.select:
                    continue
                line = self._prepare_plan_line(item, budget_plan)
                BudgetPlanLine.create(line)
        return budget_plan.id


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
    invest_asset_categ_id = fields.Many2one(
        'res.invest.asset.category',
        string='Investment Asset Category',
    )
    asset_common_name = fields.Char(
        string='Asset Common Name'
    )
    asset_name = fields.Char(
        string='Asset Name',
    )
    request_user_id = fields.Many2one(
        'hr.employee',
        string='Requester',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
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
    )
    price_unit = fields.Float(
        string='Unit Price',
    )
    price_subtotal = fields.Float(
        string='Price Subtotal',
    )
    price_other = fields.Float(
        string='Other Expenses',
    )
    price_total = fields.Float(
        string='Price Total',
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
    total_commitment = fields.Float(
        string='Total Commitment',
        readonly=True,
    )
    pr_commitment = fields.Float(
        string='PR Commitment',
        readonly=True,
    )
    exp_commitment = fields.Float(
        string='EXP Commitment',
        readonly=True,
    )
    po_commitment = fields.Float(
        string='PO Commitment',
        readonly=True,
    )
    actual_amount = fields.Float(
        string='Actual',
        readonly=True,
    )
    total_commit_and_actual = fields.Float(
        string='Total Commitment + Actual',
        readonly=True,
    )
    budget_residual = fields.Float(
        string='Residual Budget',
        readonly=True,
    )
