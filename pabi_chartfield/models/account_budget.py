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
    chart_view = fields.Selection(
        CHART_VIEW,
        string='Budget View',
        states={'done': [('readonly', True)]},
        required=True,
        copy=True,
    )

    @api.multi
    def budget_validate(self):
        for budget in self:
            line = budget.budget_line_ids
            line.validate_chartfields(self.chart_view)
        return super(AccountBudget, self).budget_validate()


class AccountBudgetLine(ChartField, models.Model):
    _inherit = 'account.budget.line'

    # Project Based
    spa_id = fields.Many2one(
        related='program_id.current_spa_id',
        readonly=True,
        store=True,
    )
    mission_id = fields.Many2one(
        related='project_id.mission_id',
        readonly=True,
        store=True,
    )
    program_scheme_id = fields.Many2one(
        related='budget_id.program_scheme_id',
        readonly=True,
        store=True,
    )
    program_group_id = fields.Many2one(
        related='budget_id.program_group_id',
        readonly=True,
        store=True,
    )
    # Unit Based
    org_id = fields.Many2one(
        related='budget_id.org_id',
        readonly=True,
        store=True,
    )
    sector_id = fields.Many2one(
        related='budget_id.sector_id',
        readonly=True,
        store=True,
    )
    division_group_id = fields.Many2one(
        related='budget_id.division_group_id',
        readonly=True,
        store=True,
    )
    division_id = fields.Many2one(
        related='budget_id.division_id',
        readonly=True,
        store=True,
    )
    department_id = fields.Many2one(
        related='budget_id.department_id',
        readonly=True,
        store=True,
    )
    costcenter_id = fields.Many2one(
        related='budget_id.costcenter_id',
        readonly=True,
        store=True,
    )
