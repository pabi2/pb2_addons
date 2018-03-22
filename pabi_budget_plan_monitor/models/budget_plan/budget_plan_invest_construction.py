# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import PrevFYCommon


class BudgetPlanInvestConstruction(models.Model):
    _inherit = 'budget.plan.invest.construction'

    @api.multi
    def compute_prev_fy_performance(self):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        PrevFY = self.env['%s.prev.fy.view' % self._name]
        PrevFY._fill_prev_fy_performance(self)  # self = plans


class BudgetPlanInvestConstructionPrevFYView(PrevFYCommon, models.Model):
    """ Prev FY Performance view, must named as [model]+perv.fy.view """
    _name = 'budget.plan.invest.construction.prev.fy.view'
    _auto = False
    _description = 'Prev FY budget performance for construction'
    # Extra variable for this view
    _chart_view = 'invest_construction'
    _ex_view_fields = ['invest_construction_id', 'org_id']
    _ex_domain_fields = ['org_id']  # Each plan is by this domain
    _ex_active_domain = \
        [('invest_construction_id.state', '=', 'approve')]
    _filter_fy = 1

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Construction',
        readonly=True,
    )

    @api.multi
    def _prepare_prev_fy_lines(self):
        """ Given search result from this view, prepare lines tuple """
        plan_lines = []
        Project = self.env['res.invest.construction']
        ProjectLine = self.env['budget.plan.invest.construction.line']
        project_fields = set(Project._fields.keys())
        plan_line_fields = set(ProjectLine._fields.keys())
        common_fields = list(project_fields & plan_line_fields)
        plan_fiscalyear_id = self._context.get('plan_fiscalyear_id')
        for rec in self:
            const = rec.invest_construction_id
            val = {
                'c_or_n': 'continue',
                'invest_construction_id': rec.invest_construction_id.id,
            }
            # Project Info, if any
            for field in common_fields:
                if field in const and \
                        field not in ['id', '__last_update',
                                      'write_uid', 'write_date',
                                      'create_uid', 'create_date',
                                      'state', 'name']:
                    try:
                        val[field] = const[field].id
                    except:
                        val[field] = const[field]

            # Next FY Commitment
            next_fy_ex = const.monitor_expense_ids.filtered(
                lambda l: l.fiscalyear_id.id == plan_fiscalyear_id)
            next_fy_commit = sum(next_fy_ex.mapped('amount_pr_commit') +
                                 next_fy_ex.mapped('amount_po_commit') +
                                 next_fy_ex.mapped('amount_exp_commit'))

            # Overall budget performance
            val.update({
                'name': const.display_name,
                'overall_released': rec.released,
                'overall_all_commit': rec.all_commit,
                'overall_pr_commit': rec.pr_commit,
                'overall_po_commit': rec.po_commit,
                'overall_exp_commit': rec.exp_commit,
                'overall_actual': rec.actual,
                'overall_consumed': rec.consumed,
                'overall_balance': rec.balance,
                'next_fy_commitment': next_fy_commit
            })
            plan_lines.append((0, 0, val))
        return plan_lines
