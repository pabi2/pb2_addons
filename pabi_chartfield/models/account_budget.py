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

    spa_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    mission_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    tag_type_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    tag_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    functional_area_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    program_group_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    # Only Program, Program Group and Project will be chosen @ header
    org_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    sector_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    department_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    division_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    section_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )
    costcenter_id = fields.Many2one(
        compute='_compute_all',
        readonly=True, store=True
    )

    @api.multi
    @api.depends('budget_id.functional_area_id',
                 'budget_id.program_group_id',
                 'budget_id.org_id',
                 'budget_id.sector_id',
                 'budget_id.department_id',
                 'budget_id.division_id',
                 'budget_id.section_id',
                 'budget_id.costcenter_id',)
    def _compute_all(self):

        for rec in self:

            # Project base, line level choose program, project_group, project
            rec.functional_area_id = rec.budget_id.functional_area_id
            rec.program_group_id = rec.budget_id.program_group_id

            # Unit base
            rec.org_id = rec.budget_id.org_id
            rec.sector_id = rec.budget_id.sector_id
            rec.department_id = rec.budget_id.department_id
            rec.division_id = rec.budget_id.division_id
            rec.section_id = rec.budget_id.section_id
            rec.costcenter_id = rec.budget_id.costcenter_id

            # Project base, more follows program, project_group, project
            if rec.budget_id.chart_view == 'project_base':
                rec.spa_id = (rec.program_id.current_spa_id)
                rec.mission_id = (rec.project_id.mission_id)
                rec.org_id = (rec.program_id.org_id or
                              rec.project_group_id.org_id or
                              rec.project_id.org_id)
                rec.tag_type_id = (rec.program_id.tag_type_id or
                                   rec.project_group_id.tag_type_id or
                                   rec.project_id.tag_type_id)
                rec.tag_id = (rec.program_id.tag_id or
                              rec.project_group_id.tag_id or
                              rec.project_id.tag_id)

            # Unit base, more dimension follows costcenter_id
            if rec.budget_id.chart_view == 'unit_base':
                rec.mission_id = rec.budget_id.costcenter_id.mission_id
