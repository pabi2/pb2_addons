# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.addons.pabi_base.models.res_common import ResCommon

from openerp.exceptions import ValidationError

# org -> sector -> subsector -> division -> *section* -> costcenter
#                                           (mission)
#
#      (type/tag)      (type/tag)   (type/tag)    (type/tag)     (type/tag)
#        (org)           (org)        (org)         (org)          (org)
# functional_area -> program_group -> program -> project_group -> *project*
#                                    (spa(s))                     (mission)
#
#     (org)
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
            'section_program_id': {},
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
                    'section_program_id': {},
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
        # 'personnel_costcenter_id': {
        #     'org_id': {},
        #     'costcenter_id': {
        #         'taxbranch_id': {}
        #     },
        # },
        'personnel_costcenter_id': {
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
        'fund_id': {}
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
                            'invest_construction_phase_id'),
}

CHART_VIEW_LIST = [(x[0], x[1][0]) for x in CHART_VIEW.items()]
CHART_VIEW_FIELD = dict([(x[0], x[1][1]) for x in CHART_VIEW.items()])

# For verification, to ensure that no field is valid outside of its view
CHART_FIELDS = [
    ('company_id', ['unit_base',
                    'project_base',
                    'personnel',
                    'invest_asset',
                    'invest_construction',
                    ]),
    ('spa_id', ['project_base']),
    ('mission_id', ['project_base',
                    'unit_base',
                    ]),  # both
    ('tag_type_id', ['project_base']),
    ('tag_id', ['project_base']),
    ('section_program_id', ['project_base',
                            'unit_base',
                            ]),  # both
    # Project Based
    ('functional_area_id', ['project_base']),
    ('program_group_id', ['project_base']),
    ('program_id', ['project_base']),
    ('project_group_id', ['project_base']),
    ('project_id', ['project_base']),
    # Unit Based
    ('org_id', ['unit_base',
                'project_base',
                'personnel',
                'invest_asset',
                'invest_construction',
                ]),  # All
    ('sector_id', ['unit_base',
                   ]),
    ('subsector_id', ['unit_base',
                      ]),
    ('division_id', ['unit_base',
                     ]),
    ('section_id', ['unit_base',
                    ]),
    ('costcenter_id', ['unit_base',
                       'project_base',
                       'personnel',
                       'invest_asset',
                       'invest_construction',
                       ]),
    ('taxbranch_id', ['unit_base',
                      'project_base',
                      'personnel',
                      'invest_asset',
                      'invest_construction',
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
    ('fund_id', ['unit_base',
                 'project_base',
                 'personnel',
                 'invest_asset',
                 'invest_construction',
                 ]),
]


# Extra non-binding chartfield (similar to activity)
class CostControlType(ResCommon, models.Model):
    _name = 'cost.control.type'
    _description = 'Job Order Type'

    description = fields.Text(
        string='Description',
        size=1000,
    )


class CostControl(ResCommon, models.Model):
    _name = 'cost.control'
    _inherit = ['mail.thread']
    _description = 'Job Order'

    @api.model
    def _get_owner_level_selection(self):
        selection = [
            ('org', 'Org'),
            ('sector', 'Sector'),
            ('subsector', 'Subsector'),
            ('division', 'Division'),
            ('section', 'Section'),
        ]
        return selection

    description = fields.Text(
        string='Description',
        size=1000,
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Job Order Type',
        required=True,
        track_visibility='onchange',
    )
    public = fields.Boolean(
        string="NSTDA Wide",
        copy=False,
        default=True,
        track_visibility='onchange',
    )
    owner_level = fields.Selection(
        string="Owner Level",
        selection=_get_owner_level_selection,
        copy=False,
        track_visibility='onchange',
    )
    # Unit Base
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        track_visibility='onchange',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
        track_visibility='onchange',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        track_visibility='onchange',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        track_visibility='onchange',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        track_visibility='onchange',
    )
    active = fields.Boolean(
        track_visibility='onchange',
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Job Order Name must be unique!'),
    ]

    @api.model
    def _check_access(self):
        if not self.env.user.has_group(
                'pabi_base.group_cooperate_budget')\
            and not self.env.user.has_group(
                'pabi_base.group_operating_unit_budget'):
            raise ValidationError(
                _('Sorry! \n You are not authorized to edit this field.'))
        return True

    @api.model
    def create(self, vals):
        if 'public' in vals:
            self._check_access()
        return super(CostControl, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'public' in vals:
            self._check_access()
        return super(CostControl, self).write(vals)

    @api.onchange('public')
    def _onchange_public(self):
        self.owner_level = False
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('owner_level')
    def _onchange_owner_level(self):
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False

    # @api.multi
    # def name_get(self):
    #     result = []
    #     for cc in self:
    #         result.append(
    #             (cc.id,
    #              "%s / %s" % (cc.cost_control_type_id.name or '-',
    #                           cc.name or '-')))
    #     return result


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
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('id', 'in', taxbranch_ids and "
        "taxbranch_ids[0] and taxbranch_ids[0][2] or False)]",
    )

    def _set_taxbranch_ids(self, lines):
        taxbranch_ids = list(set([x.taxbranch_id.id
                                  for x in lines if x.taxbranch_id]))
        self.len_taxbranch = len(taxbranch_ids)
        if not taxbranch_ids:  # If not tax branch at all, allow manual select
            taxbranch_ids = self.env['res.taxbranch'].search([]).ids
        self.taxbranch_ids = taxbranch_ids

    def _set_header_taxbranch_id(self):
        if len(self.taxbranch_ids) == 1:
            self.taxbranch_id = self.taxbranch_ids[0]
        if len(self.taxbranch_ids) > 1 and not self.taxbranch_id:
            self.taxbranch_id = False
        # For advance invoice, it is possible to have taxbranch_id this way
        # if len(self.taxbranch_ids) == 0:
        #     self.taxbranch_id = False

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

    # Topmost default
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=False,
    )
    # Shared by Project and Unit
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        ondelete='restrict',
    )
    section_program_id = fields.Many2one(
        'res.section.program',
        string='Section Program',
        ondelete='restrict',
    )
    # Project Base
    spa_id = fields.Many2one(
        'res.spa',
        string='SPA',
        ondelete='restrict',
    )
    tag_type_id = fields.Many2one(
        'res.tag.type',
        string='Tag Type',
        ondelete='restrict',
    )
    tag_id = fields.Many2one(
        'res.tag',
        string='Tag',
        ondelete='restrict',
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        ondelete='restrict',
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group',
        ondelete='restrict',
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        ondelete='restrict',
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group',
        ondelete='restrict',
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        ondelete='restrict',
        index=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        domain=lambda self: self._get_fund_domain(),
        ondelete='restrict',
    )
    # Unit Base
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        ondelete='restrict',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
        ondelete='restrict',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        ondelete='restrict',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        ondelete='restrict',
        index=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        ondelete='restrict',
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        ondelete='restrict',
    )
    # Personnel
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Budget',
        ondelete='restrict',
        index=True,
    )
    # Investment - Asset
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
        ondelete='restrict',
        index=True,
    )
    # Investment - Construction
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Construction',
        ondelete='restrict',
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Construction Phase',
        ondelete='restrict',
        index=True,
    )
    # Non Binding Dimension
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
        ondelete='restrict',
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Job Order Type',
        ondelete='restrict',
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
        copy=True,
    )

    # Required fields (to ensure no error onchange)
    activity_id = fields.Many2one('account.activity')
    product_id = fields.Many2one('product.product')
    account_id = fields.Many2one('account.account')

    @api.model
    def _get_fund_domain(self):
        domain_str = """
            ['|', '|', '|', '|',
            ('project_ids', 'in', [project_id or -1]),
            ('section_ids', 'in', [section_id or -1]),
            ('invest_asset_ids', 'in', [invest_asset_id or -1]),
            ('invest_construction_phase_ids', 'in',
                [invest_construction_phase_id or -1]),
            ('personnel_costcenter_ids', 'in',
                [personnel_costcenter_id or -1])]
        """
        return domain_str

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

    @api.model
    def _get_default_fund(self):
        # If that dimension have 1 funds, use that fund.
        # If that dimension have no funds, use NSTDA
        # Else return false
        fund_id = False
        funds = []
        if self.project_id:
            funds = self.project_id.fund_ids
        if self.section_id:
            funds = self.section_id.fund_ids
        if self.personnel_costcenter_id:
            funds = self.personnel_costcenter_id.fund_ids
        if self.invest_asset_id:
            funds = self.invest_asset_id.fund_ids
        if self.invest_construction_phase_id:
            funds = self.invest_construction_phase_id.fund_ids
        # Get default fund
        if len(funds) == 1:
            fund_id = funds[0].id
        else:
            fund_id = False
        return fund_id

    # Section
    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            if 'project_id' in self:
                self.project_id = False
            if 'personnel_costcenter_id' in self:
                self.personnel_costcenter_id = False
            if 'invest_asset_id' in self:
                self.invest_asset_id = False
            if 'invest_construction_phase_id' in self:
                self.invest_construction_phase_id = False
            self.fund_id = self._get_default_fund()

    # Project Base
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            if 'section_id' in self:
                self.section_id = False
            if 'personnel_costcenter_id' in self:
                self.personnel_costcenter_id = False
            if 'invest_asset_id' in self:
                self.invest_asset_id = False
            if 'invest_construction_phase_id' in self:
                self.invest_construction_phase_id = False
            self.fund_id = self._get_default_fund()

    # Personnel
    @api.onchange('personnel_costcenter_id')
    def _onchange_personnel_costcenter_id(self):
        if self.personnel_costcenter_id:
            if 'section_id' in self:
                self.section_id = False
            if 'project_id' in self:
                self.project_id = False
            if 'invest_asset_id' in self:
                self.invest_asset_id = False
            if 'invest_construction_phase_id' in self:
                self.invest_construction_phase_id = False
            self.fund_id = self._get_default_fund()

    # Investment Asset
    @api.onchange('invest_asset_id')
    def _onchange_invest_asset_id(self):
        if self.invest_asset_id:
            if 'section_id' in self:
                self.section_id = False
            if 'project_id' in self:
                self.project_id = False
            if 'personnel_costcenter_id' in self:
                self.personnel_costcenter_id = False
            if 'invest_construction_phase_id' in self:
                self.invest_construction_phase_id = False
            self.fund_id = self._get_default_fund()

    # Investment Construction
    @api.onchange('invest_construction_phase_id')
    def _onchange_invest_construction_phase_id(self):
        if self.invest_construction_phase_id:
            if 'section_id' in self:
                self.section_id = False
            if 'project_id' in self:
                self.project_id = False
            if 'invest_asset_id' in self:
                self.invest_asset_id = False
            if 'personnel_costcenter_id' in self:
                self.personnel_costcenter_id = False
            self.fund_id = self._get_default_fund()

    @api.model
    def _get_related_dimension(self, vals):
        selects = list(set(CHART_SELECT) & set(vals.keys()))
        res = {}
        if selects:
            selects = dict([(x, vals[x]) for x in selects])
            selects_no = {k: v for k, v in selects.items() if not v}
            selects_yes = {k: v for k, v in selects.items() if v}
            # update value = false first, the sequence is important
            for field, _dummy in selects_no.items():
                res.update(self._get_chained_dimension(field, clear=True))
            # res.update({'chart_view': self._get_chart_view(selects_yes)})
            for field, _dummy in selects_yes.items():
                if field in res:
                    res.pop(field)
                res.update(self._get_chained_dimension(field))
        return res

    @api.multi
    def update_related_dimension(self, vals):
        res = self._get_related_dimension(vals)
        if res:
            self.with_context(MyModelLoopBreaker=True).write(res)
            # Fund, assign default if none
            if not vals.get('fund_id', False):
                for rec in self:
                    if not rec.fund_id:
                        rec.with_context(MyModelLoopBreaker=True).\
                            write({'fund_id': rec._get_default_fund()})
        return True

    @api.model
    def _record_value_by_type(self, record, key):
        if self._fields[key].type == 'many2one':
            return record[key] and record[key].name or 'None'
        else:
            message = record[key] or 'None'  # Can be string or number
            if not isinstance(message, basestring) and \
                    str(message).isdigit():
                message = '{:,.2f}'.format(message)
            return message

    @api.model
    def _data_value_by_type(self, data, key):
        if self._fields[key].type == 'many2one':
            Model = self.env[self._fields[key].comodel_name]
            return data[key] and Model.browse(data[key]).name or 'None'
        else:
            message = data[key] or 'None'
            if not isinstance(message, basestring) and \
                    str(message).isdigit():
                message = '{:,.2f}'.format(message)
            return message

    @api.model
    def _change_content(self, vals, todos):
        """ This method is used to build log for chatter purposes """
        messages = []
        for field in todos:
            if field in vals:
                title = todos[field][0]
                res_model = todos[field][1]
                res_field = todos[field][2]
                # Case Add
                add_lines = filter(lambda x: x[0] == 0, vals[field])
                if add_lines:
                    message = '<h3>%s</h3>' % (title + ' add(s)')
                    message += '<ul>'
                    for line in add_lines:
                        res_id = line[2].get(res_field, False)
                        res = self.env[res_model].browse(res_id)
                        message += '<li><b>%s</b></li>' % (res.name, )
                    message += '</ul>'
                    messages.append(message)
                # Case Delete
                delete_lines = filter(lambda x: x[0] == 2, vals[field])
                if delete_lines:
                    message = '<h3>%s</h3>' % (title + ' delete(s)')
                    message += '<ul>'
                    for line in delete_lines:
                        xline = self.browse(line[1])
                        message += '<li><b>%s</b></li>' % xline[res_field].name
                    message += '</ul>'
                    messages.append(message)
                # Case Update
                change_lines = filter(lambda x: x[0] == 1, vals[field])
                if change_lines:
                    message = '<h3>%s</h3>' % (title + ' change(s)')
                    for line in change_lines:
                        xline = self.browse(line[1])
                        message += '<b>%s</b><ul>' % xline[res_field].name
                        for key in line[2]:
                            field_name = self._fields[key].string
                            old_val = self._record_value_by_type(xline, key)
                            new_val = self._data_value_by_type(line[2], key)
                            message += _(
                                '<li><b>%s</b>: %s → %s</li>'
                            ) % (field_name, old_val, new_val)
                        message += '</ul>'
                    messages.append(message)
        return messages


class ChartFieldAction(ChartField):
    """ Chartfield + Onchange for Document Transaction
        1) No Filter Domain from 1 field to another. Free to choose
        2) Choosing only folloiwng fields will auto populate others
            - cost_control_id (extra)
            - section_id
            - project_id
            - personnel_costcenter_id
            - invest_asset_id
            - invest_construction_id
    """

    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        compute='_compute_chart_view',
        store=True,
    )
    require_chartfield = fields.Boolean(
        string='Require Chartfield',
        compute='_compute_require_chartfield',
        store=True,
    )

    @api.multi
    @api.depends('project_id', 'section_id', 'personnel_costcenter_id',
                 'invest_asset_id', 'invest_construction_id')
    def _compute_chart_view(self):
        for rec in self:
            rec.chart_view = False
            view_set = False
            for k, v in CHART_VIEW_FIELD.items():
                if rec[v] and not view_set:
                    if not view_set:
                        rec.chart_view = k
                        view_set = True
                    else:
                        raise ValidationError(
                            _('More than 1 dimension selected'))

    @api.multi
    @api.depends('activity_id', 'product_id')
    def _compute_require_chartfield(self):
        Budget = self.env['account.budget']
        for rec in self:
            rec.require_chartfield = Budget.trx_budget_required(rec)
            if not rec.require_chartfield:
                rec.section_id = False
                rec.project_id = False
                rec.personnel_costcenter_id = False
                rec.invest_asset_id = False
                rec.invest_construction_phase_id = False
        return

    @api.multi
    def write(self, vals):
        # For balance sheet account, always set no dimension
        # Note by kittiu: NSTDA wants to remove this check, for NSTDA, it is ok
        #                 Might change in the future.
        # if vals.get('account_id', False):
        #     account = self.env['account.account'].browse(vals['account_id'])
        #     if account.user_type.report_type in ('asset', 'liability'):
        #         vals['section_id'] = False
        #         vals['project_id'] = False
        #         vals['personnel_costcenter_id'] = False
        #         vals['invest_asset_id'] = False
        #         vals['invest_construction_phase_id'] = False
        Budget = self.env['account.budget']
        if Budget.trx_budget_required(vals) == 0:  # Check vals, be specific
            vals['section_id'] = False
            vals['project_id'] = False
            vals['personnel_costcenter_id'] = False
            vals['invest_asset_id'] = False
            vals['invest_construction_phase_id'] = False
        res = super(ChartFieldAction, self).write(vals)
        if not self._context.get('MyModelLoopBreaker', False):
            self.update_related_dimension(vals)
        return res


class ChartfieldView(models.Model):
    """ Prepare this view, to be used in future module """
    _name = 'chartfield.view'
    _auto = False
    _order = 'seq, code'

    seq = fields.Integer(
        string='Sequence',
    )
    type = fields.Selection(
        [('sc:', 'Section'),
         ('pj:', 'Project'),
         ('cp:', 'Construction Phase'),
         ('ia:', 'Invest Asset'),
         ('pc:', 'Personnel'), ],
        string='Type',
    )
    model = fields.Char(
        string='Model',
    )
    id = fields.Integer(
        string='ID',
    )
    res_id = fields.Integer(
        string='Resource ID',
    )
    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
    name_short = fields.Char(
        string='Short Name',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
    )
    active = fields.Boolean(
        string='Active',
    )

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            name_short = ('name_short' in rec) and rec['name_short'] or False
            result.append((rec.id, "%s%s" %
                           (rec.code and '[' + rec.code + '] ' or '',
                            name_short or name or '')))
        return result

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        _sql = """
        select * from (
        (select 1 seq, 'sc:' as type, 'res.section' as model,
        id+1000000 as id, id as res_id, code, name,
        name_short, costcenter_id, active
        from res_section)
            union all
        (select 2 seq, 'pj:' as type, 'res.project' as model,
        id+2000000 as id, id as res_id, code, name, name_short,
        costcenter_id, active
        from res_project)
            union all
        (select 3 seq, 'cp:' as type, 'res.invest.construction.phase' as model,
        p.id+3000000 as id, p.id as res_id, p.code, c.name as name,
        phase as name_short, p.costcenter_id, p.active
        from res_invest_construction_phase p join res_invest_construction c on
        c.id = p.invest_construction_id)
            union all
        (select 4 seq, 'ia:' as type, 'res.invest.asset' as model,
        id+4000000 as id, id as res_id, code, name, name_short,
        costcenter_id, active
        from res_invest_asset)
            union all
        (select 5 seq, 'pc:' as type, 'res.personnel.costcenter' as model,
        id+5000000 as id, id as res_id, code, name, name_short,
        costcenter_id, active
        from res_personnel_costcenter)
        ) a
        """
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, _sql,))
