# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields, models
from .chartfield import CHART_VIEW_FIELD, ChartField
from lxml import etree


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

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(AccountBudget, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        FIELD_RELATION = {
            'unit_base': ['section_id',
                          'budget_line_unit_base'],
            'project_base': ['program_id',
                             'budget_line_project_base'],
            'personnel': ['personnel_costcenter_id',
                          'budget_line_personnel'],
            'invest_asset': ['org_id',
                             'budget_line_invest_asset'],
            'invest_construction': ['org_id',
                                    'budget_line_invest_construction'],
        }
        if self._context.get('default_chart_view', '') and view_type == 'form':
            budget_type = self._context['default_chart_view']
            del FIELD_RELATION[budget_type]
            doc = etree.XML(res['arch'])
            for key in FIELD_RELATION.keys():

                field_name = FIELD_RELATION[key][0]
                for node in doc.xpath("//field[@name='%s']" % field_name):
                    if (budget_type in ('invest_asset',
                                        'invest_construction') and
                            field_name == 'org_id'):
                        continue
                    node.getparent().remove(node)

                line_field_name = FIELD_RELATION[key][1]
                node_lines = doc.xpath("//field[@name='%s']" % line_field_name)
                for node_line in node_lines:
                    node_line.getparent().remove(node_line)

            res['arch'] = etree.tostring(doc)
        return res


class AccountBudgetLine(ChartField, models.Model):
    _inherit = 'account.budget.line'

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

    # === Invest Asset, Invest Construction ===
    @api.onchange('org_id')
    def _onchange_org_id(self):
        r1 = self._onchange_focus_field(focus_field='org_id',
                                        parent_field=False,
                                        child_field='invest_asset_id')
        r2 = self._onchange_focus_field(focus_field='org_id',
                                        parent_field=False,
                                        child_field='invest_construction_id')
        res = {'domain': {}}
        res['domain'].update(r1['domain'])
        res['domain'].update(r2['domain'])
        return res

    # === Personnel ===
    # Still unsure !!!
