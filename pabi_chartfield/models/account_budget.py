# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields, models
from .chartfield import CHART_VIEW_LIST, CHART_VIEW_FIELD, ChartField


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
        CHART_VIEW_LIST,
        string='Budget View',
        states={'done': [('readonly', True)]},
        required=False,
        copy=True,
    )

    @api.multi
    def budget_validate(self):
        for budget in self:
            lines = budget.budget_line_ids
            for line in lines:
                res = line.\
                    _get_chained_dimension(CHART_VIEW_FIELD[budget.chart_view])
                line.write(res)
        # kittiu: Following might not necessary as we already split chart_view
        #         for budget in self:
        #             budget.validate_chartfields(budget.chart_view)
        #             lines = budget.budget_line_ids
        #             lines.validate_chartfields(budget.chart_view)
        return super(AccountBudget, self).budget_validate()

    @api.multi
    def budget_confirm(self):
        for budget in self:
            lines = budget.budget_line_ids
            for line in lines:
                res = line.\
                    _get_chained_dimension(CHART_VIEW_FIELD[budget.chart_view])
                line.write(res)
        # kittiu: Following might not necessary as we already split chart_view
        #         for budget in self:
        #             budget.validate_chartfields(budget.chart_view)
        #             lines = budget.budget_line_ids
        #             lines.validate_chartfields(budget.chart_view)
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
    chart_view = fields.Selection(
        related='budget_id.chart_view',
        store=True,
    )

    # === Project Base ===
    @api.onchange('program_id')
    def _onchange_program_id(self):
        r1 = self._onchange_focus_field(focus_field='program_id',
                                        parent_field='program_group_id',
                                        child_field='project_group_id')
        # Additionally, dommain for child project_id
        r2 = self._onchange_focus_field(focus_field='program_id',
                                        parent_field='program_group_id',
                                        child_field='project_id')
        res = {'domain': {}}
        res['domain'].update(r1['domain'])
        res['domain'].update(r2['domain'])
        return res

    @api.onchange('project_group_id')
    def _onchange_project_group_id(self):
        res = self._onchange_focus_field(focus_field='project_group_id',
                                         parent_field='program_group_id',
                                         child_field='project_id')
        return res

    @api.onchange('project_id')
    def _onchange_project_id(self):
        res = self._onchange_focus_field(focus_field='project_id',
                                         parent_field='project_group_id',
                                         child_field=False)
        return res

    # === Unit Base ===
    # Nohting for Unit Base, as Section already the lowest

    # === Personnel, Invest Asset, Invest Construction ===
    @api.onchange('org_id')
    def _onchange_org_id(self):
        r1 = self._onchange_focus_field(focus_field='org_id',
                                        parent_field=False,
                                        child_field='personnel_costcenter_id')
        r2 = self._onchange_focus_field(focus_field='org_id',
                                        parent_field=False,
                                        child_field='invest_asset_id')
        r3 = self._onchange_focus_field(focus_field='org_id',
                                        parent_field=False,
                                        child_field='invest_construction_id')
        res = {'domain': {}}
        res['domain'].update(r1['domain'])
        res['domain'].update(r2['domain'])
        res['domain'].update(r3['domain'])
        return res
