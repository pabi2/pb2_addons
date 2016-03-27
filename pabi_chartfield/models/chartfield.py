# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, fields, models

# org -> sector -> department -> division -> section -> costcenter
#                                                       (mission)
#
#      (type/tag)      (type/tag)   (type/tag)    (type/tag)    (type/tag)
#        (org)           (org)        (org)         (org)         (org)
# program_scheme -> program_group -> program -> project_group -> project
#                                    (spa(s))                   (mission)

CHART_VIEW = [
    ('unit_base', 'Unit Based'),
    ('project_base', 'Project Based'),
    ]

CHART_FIELDS = [
    ('spa_id', ['project_base']),
    ('mission_id', ['project_base', 'unit_base']),  # both
    ('tag_type_id', ['project_base']),
    ('tag_id', ['project_base']),
    # Project Based
    ('program_scheme_id', ['project_base']),
    ('program_group_id', ['project_base']),
    ('program_id', ['project_base']),
    ('project_group_id', ['project_base']),
    ('project_id', ['project_base']),
    # Unit Based
    ('org_id', ['unit_base', 'project_base']),  # both
    ('sector_id', ['unit_base']),
    ('department_id', ['unit_base']),
    ('division_id', ['unit_base']),
    ('section_id', ['unit_base']),
    ('costcenter_id', ['unit_base']),
    ]


class ChartField(object):

    spa_id = fields.Many2one('res.spa', 'SPA')
    mission_id = fields.Many2one('res.mission', 'Mission')
    tag_type_id = fields.Many2one('res.tag.type', 'Tag Type')
    tag_id = fields.Many2one('res.tag', 'Tag')

    program_scheme_id = fields.Many2one('res.program.scheme', 'Program Scheme')
    program_group_id = fields.Many2one('res.program.group', 'Program Group')
    program_id = fields.Many2one('res.program', 'Program')
    project_group_id = fields.Many2one('res.project.group', 'Project Group')
    project_id = fields.Many2one('res.project', 'Project')

    org_id = fields.Many2one('res.org', 'Org')
    sector_id = fields.Many2one('res.sector', 'Sector')
    department_id = fields.Many2one('res.department', 'Department')
    division_id = fields.Many2one('res.division', 'Division')
    section_id = fields.Many2one('res.section', 'Section')
    costcenter_id = fields.Many2one('res.costcenter', 'Costcenter')

    @api.onchange('costcenter_id')
    def _onchange_costcenter_id(self):

        self.org_id = self.costcenter_id.org_id  # main
        self.sector_id = self.costcenter_id.sector_id  # main
        self.department_id = self.costcenter_id.department_id  # main
        self.division_id = self.costcenter_id.division_id  # main
        self.section_id = self.costcenter_id.section_id  # main
        self.costcenter_id = self.costcenter_id  # main
        self.mission_id = self.costcenter_id.mission_id

        self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):

        self.costcenter_id = False

        self.program_scheme_id = self.project_id.program_scheme_id  # main
        self.org_id = self.program_scheme_id.org_id
        self.tag_type_id = self.program_scheme_id.tag_type_id
        self.tag_id = self.program_scheme_id.tag_id

        self.program_group_id = self.project_id.program_group_id  # main
        self.org_id = self.program_group_id.org_id
        self.tag_type_id = self.program_group_id.tag_type_id
        self.tag_id = self.program_group_id.tag_id

        self.program_id = self.project_id.program_id  # main
        self.org_id = self.program_id.org_id
        self.tag_type_id = self.program_id.tag_type_id
        self.tag_id = self.program_id.tag_id
        self.spa_id = self.program_id.current_spa_id

        self.project_group_id = self.project_id.project_group_id  # main
        self.org_id = self.project_group_id.org_id
        self.tag_type_id = self.project_group_id.tag_type_id
        self.tag_id = self.project_group_id.tag_id

        self.project_id = self.project_id  # main
        self.org_id = self.project_id.org_id
        self.tag_type_id = self.project_id.tag_type_id
        self.tag_id = self.project_id.tag_id
        self.mission_id = self.project_id.mission_id

        # Tags
        self.org_id = (self.project_id.org_id or
                       self.project_group_id.org_id or
                       self.program_id.org_id or
                       self.program_group_id.org_id or
                       self.program_scheme_id.org_id)
        self.tag_type_id = (self.project_id.tag_type_id or
                            self.project_group_id.tag_type_id or
                            self.program_id.tag_type_id or
                            self.program_group_id.tag_type_id or
                            self.program_scheme_id.tag_type_id)
        self.tag_id = (self.project_id.tag_id or
                       self.project_group_id.tag_id or
                       self.program_id.tag_id or
                       self.program_group_id.tag_id or
                       self.program_scheme_id.tag_id)

    @api.multi
    def validate_chartfields(self, chart_type):
        # Only same chart type as specified will remains
        for line in self:
            for d in CHART_FIELDS:
                if chart_type not in d[1]:
                    line[d[0]] = False
