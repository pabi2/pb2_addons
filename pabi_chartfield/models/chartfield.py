# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError

# org -> sector -> subsector -> division -> *section* -> costcenter
#                                                       (mission)
#
#      (type/tag)      (type/tag)   (type/tag)    (type/tag)     (type/tag)
#        (org)           (org)        (org)         (org)          (org)
# functional_area -> program_group -> program -> project_group -> *project*
#                                    (spa(s))                     (mission)
#
#    (org)
# personnel_costcenter
#
#    (org)
#   (invest_asset_category)
# invest_asset
#
#        (org)
# invest_construction -> invest_construction_phase

CHART_VIEW = [
    ('unit_base', 'Unit Based'),
    ('project_base', 'Project Based'),
    ('personnel', 'Personnel'),
    ('invest_asset', 'Investment Asset'),
    ('invest_construction', 'Investment Construction'),
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
    ('org_id', ['unit_base', 'project_base',
                'personnel', 'invest_asset',
                'invest_construction']),  # All
    ('sector_id', ['unit_base']),
    ('subsector_id', ['unit_base']),
    ('division_id', ['unit_base']),
    ('section_id', ['unit_base']),
    ('costcenter_id', ['unit_base']),
    ('taxbranch_id', ['unit_base', 'project_base']),
    # Personnel
    ('personnel_costcenter_id', ['personnel']),
    # Investment
    # - Asset
    ('invest_asset_id', ['invest_asset']),
    # - Construction
    ('invest_construction_id', ['invest_construction']),
    ('invest_construction_phase_id', ['invest_construction']),
    # Non Binding
    ('cost_control_type_id', ['unit_base', 'project_base']),
    ('cost_control_id', ['unit_base', 'project_base']),
    ]


# Extra non-binding chartfield (similar to activity)
class CostControlType(models.Model):
    _name = 'cost.control.type'
    _description = 'Cost Control Type'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )


class CostControl(models.Model):
    _name = 'cost.control'
    _description = 'Cost Control'

    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Cost Control Type',
        required=True,
    )

    @api.multi
    def name_get(self):
        result = []
        for cc in self:
            result.append(
                (cc.id,
                 "%s / %s" % (cc.cost_control_type_id.name or '-',
                              cc.name or '-')))
        return result


class HeaderTaxBranch(object):

    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
    )

    def _check_taxbranch_id(self, lines):
        taxbranch_ids = list(set([x.taxbranch_id.id for x in lines]))
        if len(taxbranch_ids) > 1:
            raise UserError(_('Selected Section or Project will '
                              'result in multiple Tax Branches'))
        else:
            return taxbranch_ids and taxbranch_ids[0] or False


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
        # domain="[('tag_type_id', '=', tag_type_id)]",
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        # domain="[('functional_area_id', '=', functional_area_id)]",
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        # domain="[('program_group_id', '=', program_group_id)]",
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
        # domain="[('program_id', '=', program_id)]",
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
        # domain="[('org_id', '=', org_id)]",
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        # domain="[('sector_id', '=', sector_id)]",
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        # domain="[('subsector_id', '=', subsector_id)]",
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        # domain="[('section_ids', '!=', False)]",
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
    )
    # Personnel
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Costcenter',
    )
    # Investment - Asset
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
    )
    # Investment - Construction
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Construction',
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Construction Phase',
    )
    # Non Binding
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Cost Control',
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Cost Control Type',
    )

    # Unit Base
    @api.onchange('section_id')
    def _onchange_cost_control_id(self):
        self.cost_control_type_id = self.cost_control_id.cost_control_type_id

    @api.onchange('section_id')
    def _onchange_section_id(self):

        if self.section_id:
            self.project_id = False
            self.personnel_costcenter_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

        self.org_id = self.section_id.org_id  # main
        self.sector_id = self.section_id.sector_id  # main
        self.subsector_id = self.section_id.subsector_id  # main
        self.division_id = self.section_id.division_id  # main
        self.costcenter_id = self.section_id.costcenter_id  # main

    @api.onchange('costcenter_id')
    def _onchange_costcenter_id(self):

        if self.costcenter_id:
            self.project_id = False
            self.personnel_costcenter_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

        if len(self.costcenter_id.section_ids) > 1:
            raise UserError(_('More than 1 sections is using this costcenter'))

        self.section_id = len(self.costcenter_id.section_ids) == 1 and \
            self.costcenter_id.section_ids[0]  # main
        self.taxbranch_id = self.costcenter_id.taxbranch_id

        self.mission_id = self.costcenter_id.mission_id

    # Project Base
    @api.onchange('project_id')
    def _onchange_project_id(self):

        if self.project_id:
            self.section_id = False
            self.costcenter_id = False
            self.personnel_costcenter_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

        self.functional_area_id = self.project_id.functional_area_id  # main

        self.program_group_id = self.project_id.program_group_id  # main

        self.program_id = self.project_id.program_id  # main
        self.spa_id = self.program_id.current_spa_id

        self.project_group_id = self.project_id.project_group_id  # main

        self.project_id = self.project_id  # main
        self.taxbranch_id = self.project_id.costcenter_id.taxbranch_id
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

    # Personnel
    @api.onchange('personnel_costcenter_id')
    def _onchange_personnel_costcenter_id(self):

        if self.personnel_costcenter_id:
            self.section_id = False
            self.costcenter_id = False
            self.project_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

        self.org_id = self.personnel_costcenter_id.org_id

    # Investment Asset
    @api.onchange('invest_asset_id')
    def _onchange_invest_asset_id(self):

        if self.invest_asset_id:
            self.section_id = False
            self.costcenter_id = False
            self.project_id = False
            self.personnel_costcenter_id = False
            self.invest_construction_phase_id = False

        self.org_id = self.invest_asset_id.org_id

    # Investment Construction
    @api.onchange('invest_construction_phase_id')
    def _onchange_invest_construction_phase_id(self):

        if self.invest_construction_phase_id:
            self.section_id = False
            self.costcenter_id = False
            self.project_id = False
            self.invest_asset_id = False
            self.personnel_costcenter_id = False

        self.invest_construction_id = \
            self.invest_construction_phase_id.invest_construction_id

        self.org_id = self.invest_construction_id.org_id

    @api.multi
    def validate_chartfields(self, chart_type):
        # Only same chart type as specified will remains
        for line in self:
            for d in CHART_FIELDS:
                if chart_type not in d[1]:
                    line[d[0]] = False
