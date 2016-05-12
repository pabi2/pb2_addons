# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields, models
from .chartfield import CHART_VIEW, ChartField


class AccountBudget(ChartField, models.Model):
    _inherit = 'account.budget'

    budget_line_unit_base = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    budget_line_project_base = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    budget_line_personnel = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    budget_line_invest_asset = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    budget_line_invest_construction = fields.One2many(
        'account.budget.line',
        'budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    chart_view = fields.Selection(
        CHART_VIEW,
        string='Budget View',
        states={'done': [('readonly', True)]},
        required=False,
        copy=True,
    )

    @api.multi
    def budget_validate(self):
        for budget in self:
            budget.validate_chartfields(self.chart_view)
            line = budget.budget_line_ids
            line.validate_chartfields(self.chart_view)
        return super(AccountBudget, self).budget_validate()

    @api.multi
    def budget_confirm(self):
        for budget in self:
            budget.validate_chartfields(self.chart_view)
            line = budget.budget_line_ids
            line.validate_chartfields(self.chart_view)
        return super(AccountBudget, self).budget_confirm()


class AccountBudgetLine(ChartField, models.Model):
    _inherit = 'account.budget.line'

    section_id = fields.Many2one(
        default=lambda self: self._context.get('section_id'),
    )
    project_id = fields.Many2one(
        default=lambda self: self._context.get('project_id'),
    )
