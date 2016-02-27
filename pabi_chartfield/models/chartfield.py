# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields


CHART_VIEW = [
    ('unit_base', 'Unit Based'),
    ('project_base', 'Project Based'),
    ]

# The order must order from smaller to bigger
CHART_FIELDS = [
    ('mission_id', ['unit_base', 'project_base']),
    ('spa_id', ['project_base']),
    ('program_base_type_id', ['unit_base', 'project_base']),
    ('program_type_id', ['unit_base', 'project_base']),
    ('program_id', ['unit_base', 'project_base']),
    ('org_id', ['unit_base', 'project_base']),
    ('project_id', ['project_base']),
    ('division_id', ['unit_base']),
    ('department_id', ['unit_base']),
    ('costcenter_id', ['unit_base']),
    ]


class ChartField(object):

    mission_id = fields.Many2one('res.mission', 'Mission')
    spa_id = fields.Many2one('res.program.spa', 'SPA')
    program_base_type_id = fields.Many2one('res.program.base.type',
                                           'Program Base Type')
    program_type_id = fields.Many2one('res.program.type', 'Program Type')
    program_id = fields.Many2one('res.program', 'Program')
    org_id = fields.Many2one('res.org', 'Org')
    project_id = fields.Many2one('res.project', 'Project')
    division_id = fields.Many2one('res.division', 'Division')
    department_id = fields.Many2one('res.department', 'Department')
    costcenter_id = fields.Many2one('res.costcenter', 'Costcenter')

    @api.multi
    def validate_chartfields(self, chart_type):
        # Only same chart type as specified will remains
        for line in self:
            for d in CHART_FIELDS:
                if chart_type not in d[1]:
                    line[d[0]] = False
