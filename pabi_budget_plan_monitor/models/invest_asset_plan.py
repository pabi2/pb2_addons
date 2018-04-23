# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .budget_plan_common import PrevFYCommon


class InvestAssetPlan(models.Model):
    _inherit = 'invest.asset.plan'

    @api.multi
    def compute_prev_fy_performance(self):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        PrevFY = self.env['%s.prev.fy.view' % self._name]
        PrevFY._fill_prev_fy_performance(self)  # self = plans


class InvestAssetPlanPrevFYView(PrevFYCommon, models.Model):
    """ Prev FY Performance view, must named as [model]+perv.fy.view """
    _name = 'invest.asset.plan.prev.fy.view'
    _auto = False
    _description = 'Prev FY budget performance for invest asset'
    # Extra variable for this view
    _chart_view = 'invest_asset'
    _ex_view_fields = ['org_id', 'invest_asset_id']
    _ex_domain_fields = ['org_id']  # Each plan is by this domain of view
    _ex_active_domain = ['|', ('all_commit', '>', 0.0),
                         ('carry_forward', '>', 0.0)]
    _filter_fy = 1  # Will the result of his view focus on prev fy only

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
        readonly=True,
    )

    @api.multi
    def _prepare_prev_fy_lines(self):
        """ Given search result from this view, prepare lines tuple """
        plan_lines = []
        plan_fiscalyear_id = self._context.get('plan_fiscalyear_id')
        for rec in self:
            a = rec.invest_asset_id
            expenses = a.monitor_expense_ids
            # All actuals in the past
            all_actual = sum(expenses.mapped('amount_actual'))
            # All commitment, now and futures
            all_time_commit = sum(expenses.mapped('amount_pr_commit') +
                                  expenses.mapped('amount_po_commit') +
                                  expenses.mapped('amount_exp_commit'))
            # Next FY PR/PO/EX
            next_fy_ex = expenses.filtered(
                lambda l: l.fiscalyear_id.id == plan_fiscalyear_id)
            next_fy_commit = sum(next_fy_ex.mapped('amount_pr_commit') +
                                 next_fy_ex.mapped('amount_po_commit') +
                                 next_fy_ex.mapped('amount_exp_commit'))

            val = {
                'select': True,
                'approved': True,
                'priority': 0,
                'invest_asset_id': a.id,
                # Prev FY actual = all actual - current actal
                'prev_fy_actual': all_actual - rec.actual,
                'amount_plan': rec.released,
                'pr_commitment': rec.pr_commit,
                'exp_commitment': rec.exp_commit,
                'po_commitment': rec.po_commit,
                'total_commitment': rec.all_commit,  # Currenty year commit
                'actual_amount': rec.actual,
                'budget_usage': rec.consumed,
                'budget_remaining': rec.balance,
                'budget_carry_forward': rec.carry_forward,
                'next_fy_commitment': next_fy_commit,
                'next_accum_commitment':
                all_time_commit - rec.all_commit - next_fy_commit,
            }
            # Get asset info too.
            val.update(a._invest_asset_common_dict())
            # --
            plan_lines.append((0, 0, val))
        # ------------------------------------------------------------------
        # Additional requirement to also list all assets, not in monitoring
        # Those assets w/o code (code is generated on control activation)
        excl_asset_ids = self.mapped('invest_asset_id').ids
        incl_org_ids = self.mapped('org_id').ids
        extra_assets = self.env['res.invest.asset'].search([
            ('code', '=', False),  # No code
            ('id', 'not in', excl_asset_ids),  # Not already pulled
            ('org_id', 'in', incl_org_ids),  # in correct org
        ])
        for a in extra_assets:
            val = {
                'select': False,
                'approved': False,
                'priority': 999,
                'invest_asset_id': a.id,
                # Prev FY actual = all actual - current actal
            }
            val.update(a._invest_asset_common_dict())
            plan_lines.append((0, 0, val))
        # ------------------------------------------------------------------
        return plan_lines
