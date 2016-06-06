# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError

# org -> sector -> subsector -> division -> *section* -> costcenter
#                                           (mission)
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
#   (invest_asset_categ)  # not dimension
# invest_asset
#
#        (org)
# invest_construction -> invest_construction_phase


def _loop_structure(res, rec, d, field, clear=False):
    """ Loop through CHART_STRUCTURE to get the chained data """

    if clear or (field not in rec):
        res.update({field: False})
    elif rec[field]:
        res.update({field: rec[field].id})

    for k, _dummy in d[field].iteritems():
        if isinstance(d, dict):
            if rec[field]:
                _loop_structure(res, rec[field], d[field], k, clear)
            else:
                _loop_structure(res, rec, d[field], k, clear)


CHART_STRUCTURE = \
    {
        'section_id': {
            'division_id': {
                'subsector_id': {
                    'sector_id': {
                        'org_id': {}
                    },
                },
            },
            'mission_id': {},
            'costcenter_id': {
                'taxbranch_id': {}
            },
        },
        'project_id': {
            'project_group_id': {
                'program_id': {
                    'program_group_id': {
                        'functional_area_id': {},
                        'org_id': {},
                        'tag_id': {
                            'tag_type_id': {}
                        },
                    },
                    'org_id': {},
                    'tag_id': {
                        'tag_type_id': {}
                    },
                },
                'org_id': {},
                'tag_id': {
                    'tag_type_id': {}
                },
            },
            'org_id': {},
            'tag_id': {
                'tag_type_id': {}
            },
            'mission_id': {},
            'costcenter_id': {
                'taxbranch_id': {}
            },
        },
        'personnel_costcenter_id': {
            'org_id': {},
        },
        'invest_asset_id': {
            'org_id': {},
        },
        'invest_construction_phase_id': {
            'invest_construction_id': {
                'org_id': {},
            },
        },
        'cost_control_id': {
            'cost_control_type_id': {},
        },
    }


# Budget structure and its selection field in document)
# Only following field will be visible for selection
# Only 1 field in a group can exists together
CHART_SELECT = [
    'section_id',  # Binding
    'project_id',
    'personnel_costcenter_id',
    'invest_asset_id',
    'invest_construction_phase_id',
    'cost_control_id',  # Non-Binding
    ]

# All types of budget structure
# This is related to chart structure
CHART_VIEW = {
    'unit_base': ('Unit Based', 'section_id'),
    'project_base': ('Project Based', 'project_id'),
    'personnel': ('Personnel', 'personnel_costcenter_id'),
    'invest_asset': ('Investment Asset', 'invest_asset_id'),
    'invest_construction': ('Investment Construction',
                            'invest_construction_id'),
    }

CHART_VIEW_LIST = [(x[0], x[1][0]) for x in CHART_VIEW.items()]
CHART_VIEW_FIELD = dict([(x[0], x[1][1]) for x in CHART_VIEW.items()])

# For verification, to ensure that no field is valid outside of its view
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
    # Non Binding Dimension
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Cost Control',
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Cost Control Type',
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        states={'done': [('readonly', True)]},
        required=False,
        copy=True,
    )

    @api.multi
    def validate_chartfields(self, chart_type):
        # Only same chart type as specified will remains
        for line in self:
            for d in CHART_FIELDS:
                if chart_type not in d[1]:
                    line[d[0]] = False

    @api.model
    def _get_chained_dimension(self, field, clear=False):
        """ This method will use CHART_STRUCTURE to prepare data """
        res = {}
        _loop_structure(res, self, CHART_STRUCTURE, field, clear=clear)
        if field in res:
            res.pop(field)  # To avoid recursive
        return res


class ChartFieldAction(ChartField):
    """ Chartfield + Onchange for Document Transaction
        1) No Filter Domain from 1 field to another. Free to choose
        2) Choosing only folloiwng fields will auto populate others
            - const_control_id (extra)
            - section_id
            - project_id
            - personnel_costcenter_id
            - invest_asset_id
            - invest_construction_id
    """
    @api.multi
    def write(self, vals):
        res = super(ChartFieldAction, self).write(vals)
        self.update_related_dimension(vals)
        return res

    @api.model
    def create(self, vals):
        res = super(ChartFieldAction, self).create(vals)
        res.update_related_dimension(vals)
        return res

    @api.v7
    def create(self, cr, uid, vals, context=None):
        new_id = super(ChartFieldAction, self).create(cr, uid, vals,
                                                      context=context)
        self.update_related_dimension(cr, uid, [new_id], vals)
        return new_id

    @api.model
    def _get_chart_view(self, selects_yes):
        # update chart_view
        chart_view = False
        assert len(selects_yes.keys()) <= 1, 'Only 1 chart_view allowed!'
        if selects_yes.keys():
            selected_field = selects_yes.keys()[0]
            for key, value in CHART_VIEW_FIELD.items():
                if value == selected_field:
                    chart_view = key
        return chart_view

    @api.multi
    def update_related_dimension(self, vals):
        # Find selected dimension that is in CHART_SELECT list
        selects = list(set(CHART_SELECT) & set(vals.keys()))
        if selects:
            selects = dict([(x, vals[x]) for x in selects])
            selects_no = {k: v for k, v in selects.items() if not v}
            selects_yes = {k: v for k, v in selects.items() if v}
            # update value = false first, the sequence is important
            for field, _dummy in selects_no.items():
                res = self._get_chained_dimension(field, clear=True)
                res.update({'chart_view': False})
                self.write(res)
            for field, _dummy in selects_yes.items():
                res = self._get_chained_dimension(field)
                res.update({'chart_view': self._get_chart_view(selects_yes)})
                self.write(res)

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.project_id = False
            self.personnel_costcenter_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

    # Project Base
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.section_id = False
            self.personnel_costcenter_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

    # Personnel
    @api.onchange('personnel_costcenter_id')
    def _onchange_personnel_costcenter_id(self):
        if self.personnel_costcenter_id:
            self.section_id = False
            self.project_id = False
            self.invest_asset_id = False
            self.invest_construction_phase_id = False

    # Investment Asset
    @api.onchange('invest_asset_id')
    def _onchange_invest_asset_id(self):
        if self.invest_asset_id:
            self.section_id = False
            self.project_id = False
            self.personnel_costcenter_id = False
            self.invest_construction_phase_id = False

    # Investment Construction
    @api.onchange('invest_construction_phase_id')
    def _onchange_invest_construction_phase_id(self):
        if self.invest_construction_phase_id:
            self.section_id = False
            self.project_id = False
            self.invest_asset_id = False
            self.personnel_costcenter_id = False
