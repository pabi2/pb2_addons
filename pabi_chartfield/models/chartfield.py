# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields, models


CHART_VIEW = [
    ('unit_base', 'Unit Based'),
    ('project_base', 'Project Based'),
    ]

CHART_FIELDS = [
    # Project Based
    ('spa_id', ['project_base']),
    ('mission_id', ['project_base']),
    ('program_scheme_id', ['project_base']),
    ('program_group_id', ['project_base']),
    ('program_id', ['project_base']),
    ('project_group_id', ['project_base']),
    ('project_id', ['project_base']),
    # Unit Based
    ('org_id', ['unit_base']),
    ('sector_id', ['unit_base']),
    ('division_group_id', ['unit_base']),
    ('division_id', ['unit_base']),
    ('department_id', ['unit_base']),
    ('costcenter_id', ['unit_base']),
    ]


class ChartField(object):

    spa_id = fields.Many2one('res.spa', 'SPA')
    mission_id = fields.Many2one('res.mission', 'Mission')
    program_scheme_id = fields.Many2one('res.program.scheme', 'Program Scheme')
    program_group_id = fields.Many2one('res.program.group', 'Program Group')
    program_id = fields.Many2one('res.program', 'Program')
    project_group_id = fields.Many2one('res.project.group', 'Project Group')
    project_id = fields.Many2one('res.project', 'Project')

    org_id = fields.Many2one('res.org', 'Org')
    sector_id = fields.Many2one('res.sector', 'Sector')
    division_group_id = fields.Many2one('res.division.group', 'Division Group')
    division_id = fields.Many2one('res.division', 'Division')
    department_id = fields.Many2one('res.department', 'Department')
    costcenter_id = fields.Many2one('res.costcenter', 'Costcenter')

    @api.onchange('costcenter_id')
    def _onchange_costcenter_id(self):

        self.org_id = self.costcenter_id.org_id
        self.sector_id = self.costcenter_id.sector_id
        self.division_group_id = self.costcenter_id.division_group_id
        self.division_id = self.costcenter_id.division_id
        self.department_id = self.costcenter_id.department_id
        self.costcenter_id = self.costcenter_id

        self.spa_id = False
        self.mission_id = False
        self.program_scheme_id = False
        self.program_group_id = False
        self.program_id = False
        self.project_group_id = False
        self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):

        self.org_id = False
        self.sector_id = False
        self.division_group_id = False
        self.division_id = False
        self.department_id = False
        self.costcenter_id = False

        self.spa_id = self.project_id.program_id.current_spa_id
        self.mission_id = self.project_id.mission_id
        self.program_scheme_id = self.project_id.program_scheme_id
        self.program_group_id = self.project_id.program_group_id
        self.program_id = self.project_id.program_id
        self.project_group_id = self.project_id.project_group_id
        self.project_id = self.project_id

    @api.multi
    def validate_chartfields(self, chart_type):
        # Only same chart type as specified will remains
        for line in self:
            for d in CHART_FIELDS:
                if chart_type not in d[1]:
                    line[d[0]] = False
