# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields
from openerp.addons.pabi_base.models.res_common import ResCommon

# org -> sector -> subsector -> division -> *section* -> costcenter
#                                           (mission)
#
#      (type/tag)      (type/tag)   (type/tag)    (type/tag)     (type/tag)
#        (org)           (org)        (org)         (org)          (org)
# functional_area -> program_group -> program -> project_group -> *project*
#                                    (spa(s))                     (mission)
#
#    (section)
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
        },
        'invest_asset_id': {
            'costcenter_id': {
                'taxbranch_id': {}
            },
            'org_id': {},
        },
        'invest_construction_phase_id': {
            'invest_construction_id': {
                'costcenter_id': {
                    'taxbranch_id': {}
                },
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
    ('mission_id', ['project_base',
                    'unit_base',
                    'personnel',
                    ]),  # both
    ('tag_type_id', ['project_base']),
    ('tag_id', ['project_base']),
    # Project Based
    ('functional_area_id', ['project_base']),
    ('program_group_id', ['project_base']),
    ('program_id', ['project_base']),
    ('project_group_id', ['project_base']),
    ('project_id', ['project_base']),
    ('fund_id', ['project_base']),
    # Unit Based
    ('org_id', ['unit_base',
                'project_base',
                'personnel',
                'invest_asset',
                'invest_construction',
                ]),  # All
    ('sector_id', ['unit_base',
                   'personnel',
                   ]),
    ('subsector_id', ['unit_base',
                      'personnel',
                      ]),
    ('division_id', ['unit_base',
                     'personnel',
                     ]),
    ('section_id', ['unit_base',
                    'personnel',
                    ]),
    ('costcenter_id', ['unit_base',
                       'personnel',
                       ]),
    ('taxbranch_id', ['unit_base',
                      'project_base',
                      'personnel',
                      ]),
    # Personnel
    ('personnel_costcenter_id', ['personnel']),
    # Investment
    # - Asset
    ('invest_asset_id', ['invest_asset']),
    # - Construction
    ('invest_construction_id', ['invest_construction']),
    ('invest_construction_phase_id', ['invest_construction']),
    # Non Binding
    ('cost_control_type_id', ['unit_base',
                              'project_base',
                              'personnel',
                              ]),
    ('cost_control_id', ['unit_base',
                         'project_base',
                         'personnel',
                         ]),
    ]


# Extra non-binding chartfield (similar to activity)
class CostControlType(ResCommon, models.Model):
    _name = 'cost.control.type'
    _description = 'Cost Control Type'

    description = fields.Text(
        string='Description',
    )


class CostControl(ResCommon, models.Model):
    _name = 'cost.control'
    _description = 'Cost Control'

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

    taxbranch_ids = fields.Many2many(
        'res.taxbranch',
        string='Tax Branches',
        help="This field store available taxbranch of this document",
    )
    len_taxbranch = fields.Integer(
        string='Len Tax Branches',
        help="Special field, used just to set field as Tax Branch required",
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        domain="[('id', 'in', taxbranch_ids and "
        "taxbranch_ids[0] and taxbranch_ids[0][2] or False)]",
    )

    def _set_taxbranch_ids(self, lines):
        taxbranch_ids = list(set([x.taxbranch_id.id
                                  for x in lines if x.taxbranch_id]))
        self.taxbranch_ids = taxbranch_ids
        self.len_taxbranch = len(taxbranch_ids)

    def _set_header_taxbranch_id(self):
        if len(self.taxbranch_ids) == 1:
            self.taxbranch_id = self.taxbranch_ids[0]
        if len(self.taxbranch_ids) > 1 and not self.taxbranch_id:
            self.taxbranch_id = False
        if len(self.taxbranch_ids) == 0:
            self.taxbranch_id = False

    @api.multi
    def write(self, vals):
        res = super(HeaderTaxBranch, self).write(vals)
        if self.env.context.get('MyModelLoopBreaker'):
            return res
        self = self.with_context(MyModelLoopBreaker=True)
        for rec in self:
            rec._set_header_taxbranch_id()
        return res


class ChartField(object):

    # Project Base
    spa_id = fields.Many2one(
        'res.spa',
        string='SPA',
        default=lambda self: self.env['res.spa'].
        browse(self._context.get('spa_id')),
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        default=lambda self: self.env['res.mission'].
        browse(self._context.get('mission_id')),
    )
    tag_type_id = fields.Many2one(
        'res.tag.type',
        string='Tag Type',
        default=lambda self: self.env['res.tag.type'].
        browse(self._context.get('tag_type_id')),
    )
    tag_id = fields.Many2one(
        'res.tag',
        string='Tag',
        default=lambda self: self.env['res.tag'].
        browse(self._context.get('tag_id')),
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        default=lambda self: self.env['res.functional.area'].
        browse(self._context.get('functional_area_id')),
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        default=lambda self: self.env['res.program.group'].
        browse(self._context.get('program_group_id')),
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        default=lambda self: self.env['res.program'].
        browse(self._context.get('program_id')),
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
        default=lambda self: self.env['res.project.group'].
        browse(self._context.get('project_group_id')),
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        default=lambda self: self.env['res.project'].
        browse(self._context.get('project_id')),
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        domain="['|', '|', '|', '|',"
        "('project_ids', 'in', [project_id or 0]),"
        "('section_ids', 'in', [section_id or 0]),"
        "('invest_asset_ids', 'in', [invest_asset_id or 0]),"
        "('invest_construction_phase_ids', 'in', "
        "[invest_construction_phase_id or 0]),"
        "('personnel_costcenter_ids', 'in', [personnel_costcenter_id or 0]),"
        "]",
    )
    # Unit Base
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        default=lambda self: self.env['res.org'].
        browse(self._context.get('org_id')),
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
        default=lambda self: self.env['res.sector'].
        browse(self._context.get('sector_id')),
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        default=lambda self: self.env['res.subsector'].
        browse(self._context.get('subsector_id')),
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        default=lambda self: self.env['res.division'].
        browse(self._context.get('division_id')),
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        default=lambda self: self.env['res.section'].
        browse(self._context.get('section_id')),
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        default=lambda self: self.env['res.costcenter'].
        browse(self._context.get('costcenter_id')),
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        default=lambda self: self.env['res.taxbranch'].
        browse(self._context.get('taxbranch_id')),
    )
    # Personnel
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Budget',
        default=lambda self: self.env['res.personnel.costcenter'].
        browse(self._context.get('personnel_costcenter_id')),
    )
    # Investment - Asset
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
        default=lambda self: self.env['res.invest.asset'].
        browse(self._context.get('invest_asset_id')),
    )
    # Investment - Construction
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Construction',
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Construction Phase',
        default=lambda self: self.env['res.invest.construction.phase'].
        browse(self._context.get('invest_construction_id')),
    )
    # Non Binding Dimension
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Cost Control',
        default=lambda self: self.env['cost.control'].
        browse(self._context.get('cost_control_id')),
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Cost Control Type',
        default=lambda self: self.env['cost.control.type'].
        browse(self._context.get('cost_control_type_id')),
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
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

    require_chartfield = fields.Boolean(
        string='Require Chartfield',
        compute='_compute_require_chartfield',
    )

    @api.multi
    @api.depends('activity_id', 'product_id')
    def _compute_require_chartfield(self):
        for rec in self:
            if 'activity_id' in rec and rec.activity_group_id:
                report_type = rec.activity_id.\
                    account_id.user_type.report_type
                rec.require_chartfield = report_type not in ('asset',
                                                             'liability')
            else:
                rec.require_chartfield = True
            if not rec.require_chartfield:
                rec.section_id = False
                rec.project_id = False
                rec.personnel_costcenter_id = False
                rec.invest_asset_id = False
                rec.invest_construction_phase_id = False
        return

    @api.multi
    def write(self, vals):
        res = super(ChartFieldAction, self).write(vals)
        if not self._context.get('update_dimension', False):
            self.update_related_dimension(vals)
        return res

    @api.model
    def _get_chart_view(self, selects_yes):
        # update chart_view
        chart_view = False
        keys = list(set(selects_yes.keys()) & set(CHART_VIEW_FIELD.values()))
        assert len(keys) <= 1, 'Only 1 chart_view allowed!'
        if selects_yes.keys():
            selected_field = selects_yes.keys()[0]
            for k, v in CHART_VIEW_FIELD.items():
                if v == selected_field:
                    chart_view = k
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
            res = {}
            for field, _dummy in selects_no.items():
                res.update(self._get_chained_dimension(field, clear=True))
            res.update({'chart_view': self._get_chart_view(selects_yes)})
            for field, _dummy in selects_yes.items():
                if field in res:
                    res.pop(field)
                res.update(self._get_chained_dimension(field))
            self.with_context(update_dimension=True).write(res)

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
