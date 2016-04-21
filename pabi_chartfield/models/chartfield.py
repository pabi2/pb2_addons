# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError

# org -> sector -> subsector -> division -> section -> costcenter
#                                                       (mission)
#
#      (type/tag)      (type/tag)   (type/tag)    (type/tag)    (type/tag)
#        (org)           (org)        (org)         (org)         (org)
# functional_area -> program_group -> program -> project_group -> project
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
    ('functional_area_id', ['project_base']),
    ('program_group_id', ['project_base']),
    ('program_id', ['project_base']),
    ('project_group_id', ['project_base']),
    ('project_id', ['project_base']),
    # Unit Based
    ('org_id', ['unit_base', 'project_base']),  # both
    ('sector_id', ['unit_base']),
    ('subsector_id', ['unit_base']),
    ('division_id', ['unit_base']),
    ('section_id', ['unit_base']),
    ('costcenter_id', ['unit_base']),
    # Non Binding
    ('nstda_course_id', ['unit_base', 'project_base']),
    ]


# Extra non-binding chartfield (similar to activity)
class NSTDACourse(models.Model):
    _name = 'nstda.course'
    _description = 'NSTDA Courses'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )


class ChartField(object):

    # Project Base
    spa_id = fields.Many2one(
        'res.spa',
        string='SPA',
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
    )
    tag_type_id = fields.Many2one(
        'res.tag.type',
        string='Tag Type',
    )
    tag_id = fields.Many2one(
        'res.tag',
        string='Tag',
        domain="[('tag_type_id', '=', tag_type_id)]",
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        domain="[('functional_area_id', '=', functional_area_id)]",
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        domain="[('program_group_id', '=', program_group_id)]",
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
        domain="[('program_id', '=', program_id)]",
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
    )
    # Unit Base
    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
        domain="[('org_id', '=', org_id)]",
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        domain="[('sector_id', '=', sector_id)]",
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        domain="[('subsector_id', '=', subsector_id)]",
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        domain="[('section_ids', '!=', False)]",
    )
    # Non Binding
    nstda_course_id = fields.Many2one(
        'nstda.course',
        string='NSTDA Course',
    )

    @api.onchange('section_id')
    def _onchange_section_id(self):

        self.org_id = self.section_id.org_id  # main
        self.sector_id = self.section_id.sector_id  # main
        self.subsector_id = self.section_id.subsector_id  # main
        self.division_id = self.section_id.division_id  # main
        self.costcenter_id = self.section_id.costcenter_id  # main

        self.project_id = False

    @api.onchange('costcenter_id')
    def _onchange_costcenter_id(self):
        if len(self.costcenter_id.section_ids) > 1:
            raise UserError(_('More than 1 sections is using this costcenter'))

        self.section_id = len(self.costcenter_id.section_ids) == 1 and \
            self.costcenter_id.section_ids[0]  # main
        self.mission_id = self.costcenter_id.mission_id

        self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):

        self.section_id = False
        self.costcenter_id = False

        self.functional_area_id = self.project_id.functional_area_id  # main
        self.org_id = self.functional_area_id.org_id
        self.tag_type_id = self.functional_area_id.tag_type_id
        self.tag_id = self.functional_area_id.tag_id

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
                       self.functional_area_id.org_id)
        self.tag_type_id = (self.project_id.tag_type_id or
                            self.project_group_id.tag_type_id or
                            self.program_id.tag_type_id or
                            self.program_group_id.tag_type_id or
                            self.functional_area_id.tag_type_id)
        self.tag_id = (self.project_id.tag_id or
                       self.project_group_id.tag_id or
                       self.program_id.tag_id or
                       self.program_group_id.tag_id or
                       self.functional_area_id.tag_id)

    @api.multi
    def validate_chartfields(self, chart_type):
        # Only same chart type as specified will remains
        for line in self:
            for d in CHART_FIELDS:
                if chart_type not in d[1]:
                    line[d[0]] = False
