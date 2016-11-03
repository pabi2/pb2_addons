# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import \
    models, fields, api
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField


class BudgetPlan(models.Model):
    _inherit = 'budget.plan.unit'

    plan_history_line_ids = fields.One2many(
        'budget.plan.history',
        'plan_id',
        string="Budget Plan History",
    )


class BudgetPlanLine(models.Model):
    _inherit = 'budget.plan.unit.line'

    activity_unit_price = fields.Float(
        string="Unit Price",
    )
    activity_unit = fields.Float(
        string="Activity Unit",
    )
    unit = fields.Float(
        string="Unit",
    )
    total_budget = fields.Float(
        string="Total Budget",
        compute="_compute_total_budget",
    )

    @api.depends('unit',
                 'activity_unit',
                 'activity_unit_price')
    def _compute_total_budget(self):
        for line in self:
            line.total_budget =\
                line.unit * line.activity_unit * line.activity_unit_price


class AccountBudgetLine(ChartField, models.Model):
    _inherit = 'account.budget.line'

    display_name = fields.Char(
        string='Display Name',
        readonly=True,
        compute='_compute_display_name',
    )

    @api.multi
    @api.depends()
    def _compute_display_name(self):
        for rec in self:
            if rec.activity_id:
                rec.display_name = rec.activity_id.name
                continue
            if rec.activity_group_id:
                rec.display_name = rec.activity_group_id.name
                continue
            for chartfield in CHART_FIELDS:
                if rec[chartfield[0]]:
                    rec.display_name = rec[chartfield[0]].name
                    break
