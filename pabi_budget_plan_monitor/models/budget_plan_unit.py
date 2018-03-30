# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import PrevFYCommon


class BudgetPlanUnit(models.Model):
    _inherit = 'budget.plan.unit'

    @api.multi
    def compute_prev_fy_performance(self):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        PrevFY = self.env['%s.prev.fy.view' % self._name]
        PrevFY._fill_prev_fy_performance(self)  # self = plans


class BudgetPlanUnitPrevFYView(PrevFYCommon, models.Model):
    """ Prev FY Performance view, must named as [model]+perv.fy.view """
    _name = 'budget.plan.unit.prev.fy.view'
    _auto = False
    _description = 'Prev FY budget performance for project base'
    # Extra variable for this view
    _chart_view = 'unit_base'
    _ex_view_fields = ['section_id', 'document',
                       'activity_group_id', 'cost_control_id']
    _ex_domain_fields = ['section_id']  # Each plan is by this domain of view
    _ex_active_domain = [('all_commit', '>', 0.0)]
    _filter_fy = 2  # Will the result of his view focus on prev fy only

    section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
    )
    document = fields.Char(
        string='Document',
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Joe Order',
        readonly=True,
    )

    @api.multi
    def _prepare_prev_fy_lines(self):
        """ Given search result from this view, prepare lines tuple """
        plan_lines = []
        prev_fy_id = self._context.get('prev_fiscalyear_id')
        plan_fy_id = self._context.get('plan_fiscalyear_id')
        plan_fy_lines = self.filtered(lambda l:
                                      l.fiscalyear_id.id == plan_fy_id)
        prev_fy_lines = self.filtered(lambda l:
                                      l.fiscalyear_id.id == prev_fy_id)
        for rec in prev_fy_lines:
            if not rec.all_commit:
                continue
            # Next FY PR/PO/EX
            plan_fy_ag_lines = plan_fy_lines.filtered(
                lambda l: l.activity_group_id == rec.activity_group_id and
                l.document == rec.document)
            next_fy_commit = sum(plan_fy_ag_lines.mapped('all_commit'))
            val = {'activity_group_id': rec.activity_group_id.id,
                   'cost_control_id': rec.cost_control_id.id,
                   'm0': rec.all_commit,
                   'next_fy_commitment': next_fy_commit,
                   'description': rec.document,
                   }
            plan_lines.append((0, 0, val))
        return plan_lines
