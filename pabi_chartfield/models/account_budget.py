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

    # TODO: When confirm budget, validate all fields has relationship


class AccountBudgetLine(ChartField, models.Model):
    _inherit = 'account.budget.line'

    # Default from header selection
    section_id = fields.Many2one(
        default=lambda self: self.env['res.section'].
        browse(self._context.get('section_id')),
    )
    program_id = fields.Many2one(
        default=lambda self: self.env['res.program'].
        browse(self._context.get('program_id')),
    )
    personnel_costcenter_id = fields.Many2one(
        default=lambda self: self.env['res.personnel.costcenter'].
        browse(self._context.get('personnel_costcenter_id')),
    )
    org_id = fields.Many2one(
        default=lambda self: self.env['res.org'].
        browse(self._context.get('org_id')),
    )

    # Domain for visible fields in budget line
    project_group_id = fields.Many2one(
        domain="[('program_id', '=', program_id)]"
    )
    project_id = fields.Many2one(
        domain="[('project_group_id', '=', project_group_id)]"
    )
    invest_asset_id = fields.Many2one(
        domain="[('org_id', '=', org_id)]"
    )
    invest_construction_id = fields.Many2one(
        domain="[('org_id', '=', org_id)]"
    )
    invest_construction_phase_id = fields.Many2one(
        domain="[('org_id', '=', org_id)]"
    )

    # Unit Based
    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.org_id = self.section_id.org_id
        self.sector_id = self.section_id.sector_id
        self.subsector_id = self.section_id.subsector_id
        self.division_id = self.section_id.division_id
        self.costcenter_id = self.section_id.costcenter_id

    # Project Based
    @api.onchange('program_id')
    def _onchange_program_id(self):
        self.program_group_id = self.program_id.program_group_id
        self.functional_area_id = self.program_id.functional_area_id

    # Personnel
    @api.onchange('personnel_costcenter_id')
    def _onchange_personnel_costcenter_id(self):
        self.org_id = self.personnel_costcenter_id.org_id
