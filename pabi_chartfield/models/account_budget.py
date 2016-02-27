# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields, models
from .chartfield import CHART_VIEW, ChartField


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    crossovered_budget_line_unit_base = fields.One2many(
        'crossovered.budget.lines',
        'crossovered_budget_id',
        string='Budget Lines',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    crossovered_budget_line_project_base = fields.One2many(
        'crossovered.budget.lines',
        'crossovered_budget_id',
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
    program_type_id = fields.Many2one(
        'res.program.type',
        string='Program Type',
        states={'done': [('readonly', True)]},
        required=True,
        copy=True,
    )
    # For unit base
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    department_id = fields.Many2one(
        'res.department',
        string='Department',
        states={'done': [('readonly', True)]},
        copy=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        states={'done': [('readonly', True)]},
        copy=True,
    )

    @api.multi
    def budget_validate(self):
        for budget in self:
            line = budget.crossovered_budget_line
            line.validate_chartfields(self.chart_view)
        return super(CrossoveredBudget, self).budget_validate()


class CrossoveredBudgetLines(ChartField, models.Model):
    _inherit = 'crossovered.budget.lines'
