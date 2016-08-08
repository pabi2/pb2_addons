# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_template import BudgetPlanCommon


class BudgetPlanInvestAsset(BudgetPlanCommon, models.Model):
    _name = 'budget.plan.invest.asset'
    _inherits = {'budget.plan.template': 'template_id'}
    _description = "Investment Asset Budget - Budget Plan"

    template_id = fields.Many2one(
        'budget.plan.template',
        required=True,
        ondelete='cascade',
    )
    plan_line_ids = fields.One2many(
        'budget.plan.invest.asset.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=False,
    )
    planned_overall = fields.Float(
        string='Budget Plan',
        compute='_compute_planned_overall',
        store=True,
    )
    asset_plan_id = fields.Many2one(
        'invest.asset.plan',
        string='Invest Asset Plan',
        readonly=True,
    )

    # Call inherited methods
    @api.multi
    def unlink(self):
        for rec in self:
            rec.plan_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPlanInvestAsset, self).unlink()

    @api.model
    def convert_plan_to_budget_control(self, active_ids):
        head_src_model = self.env['budget.plan.invest.asset']
        line_src_model = self.env['budget.plan.invest.asset.line']

        self._convert_plan_to_budget_control(active_ids,
                                             head_src_model,
                                             line_src_model)


class BudgetPlanInvestAssetLine(models.Model):
    _name = 'budget.plan.invest.asset.line'
    _inherits = {'budget.plan.line.template': 'template_id'}
    _description = "Investment Asset Budget - Budget Plan Line"

    plan_id = fields.Many2one(
        'budget.plan.invest.asset',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
        readonly=True,
    )
    template_id = fields.Many2one(
        'budget.plan.line.template',
        required=True,
        ondelete='cascade',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    info_id = fields.Many2one(
        'budget.plan.invest.asset.line.info',
        string="More Info",
        ondelete='restrict',
        readonly=True,
    )
    item_id = fields.Many2one(
        'invest.asset.plan.item',
        string='Asset Info',
        ondelete='restrict',
        readonly=True,
    )

    @api.model
    def create(self, vals):
        if not vals.get('info_id', False):
            info = self.env['budget.plan.invest.asset.line.info'].\
                create({'name': ('More...')})
            vals.update({'info_id': info.id})

        res = super(BudgetPlanInvestAssetLine, self).create(vals)
        res.write({'chart_view': res.plan_id.chart_view,
                   'fiscalyear_id': res.plan_id.fiscalyear_id.id})

        res.info_id.asset_line_id = res.id
        return res

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPlanInvestAssetLine, self).unlink()


class BudgetPlanInvestAssetLineInfo(models.Model):
    _name = 'budget.plan.invest.asset.line.info'
    _description = 'More Info about each investment asset plan line'

    asset_line_id = fields.Many2one(
        'budget.plan.invest.asset.line',
        string='Investment Asset Line',
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(
        string='Name',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
    )
    location = fields.Char(
        string='Asset Location',
    )
    quantity = fields.Float(
        string='Quantity',
    )
    price_unit = fields.Float(
        string='Unit Price',
    )
    price_subtotal = fields.Float(
        string='Quantity',
    )
    price_other = fields.Float(
        string='Other Expenses',
    )
    price_total = fields.Float(
        string='Total Price',
    )
    amount_budget = fields.Float(
        string='Budget Amount',
    )
    date_quotation = fields.Date(
        string='Quotation Date',
    )
    days_valid = fields.Integer(
        string='Validity Days'
    )
    date_quotation_valid = fields.Date(
        string='Quotation Validity Date',
    )
    reason_purchase = fields.Selection(
        [('new', 'New'),
         ('replace', 'Replacement'),
         ('extra', 'Extra')],
        string='Reason to purchase',
    )
    reason_purchase_text = fields.Text(
        string='Reason Description',
    )
    expected_result_text = fields.Text(
        string='Expected Result',
    )
    priority = fields.Integer(
        string='Priority',
    )
    request_user_id = fields.Many2one(
        'hr.employee',
        string='Requester',
    )
    planned_utilization = fields.Char(
        string='Planned Utilization',
    )
    quotation_document = fields.Char(
        string='Quotation Document',
    )
    specification_document = fields.Char(
        string='Specification Document',
    )
