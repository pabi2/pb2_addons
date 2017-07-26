# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
# from openerp.addons.document_status_history.models.document_history import \
#     LogCommon


class BudgetPlanInvestAsset(BPCommon, models.Model):
    _name = 'budget.plan.invest.asset'
    _inherit = ['mail.thread']
    _description = "Invest Asset - Budget Plan"
    _order = 'id desc'

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.invest.asset.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.invest.asset.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.invest.asset.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
        track_visibility='onchange',
    )
    # Invest Asset Only
    asset_plan_id = fields.Many2one(
        'invest.asset.plan',
        string='Invest Asset Plan',
        readonly=True,
    )
    # Select Dimension - Invest Asset
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )
    _sql_constraints = [
        ('uniq_plan', 'unique(org_id, fiscalyear_id)',
         'Duplicated budget plan for the same org is not allowed!'),
    ]

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.org', vals['org_id'])
        vals.update({'name': name})
        return super(BudgetPlanInvestAsset, self).create(vals)

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('org_id')._ids
        # Find Programs
        orgs = self.env['res.org'].search([('id', 'not in', _ids)])
        plan_ids = []
        for org in orgs:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'org_id': org.id,
                                'user_id': False})
            plan_ids.append(plan.id)
        return plan_ids

    @api.multi
    def convert_to_budget_control(self):
        """ Create a budget control from budget plan """
        self.ensure_one()
        head_src_model = self.env['budget.plan.invest.asset']
        line_src_model = self.env['budget.plan.invest.asset.line']
        budget = self._convert_plan_to_budget_control(self.id,
                                                      head_src_model,
                                                      line_src_model)
        return budget


class BudgetPlanInvestAssetLine(BPLMonthCommon, ActivityCommon, models.Model):
    _name = 'budget.plan.invest.asset.line'
    _description = "Invest Asset - Budget Plan Line"

    # COMMON
    chart_view = fields.Selection(
        default='invest_asset',  # Invest Asset
    )
    plan_id = fields.Many2one(
        'budget.plan.invest.asset',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # Extra
    org_id = fields.Many2one(
        related='plan_id.org_id',
        store=True,
        readonly=True,
    )
    item_id = fields.Many2one(
        'invest.asset.plan.item',
        string='Asset Info',
        ondelete='restrict',
        readonly=True,
    )

    # Required for updating dimension
    # FIND ONLY WHAT IS NEED AND USE related field.
