# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.addons.pabi_base.models.res_common import ResCommon
from openerp import tools

# ORG Structure:
#                                           (mission)
#                                           costcenter
#                                               o
#                                               |
#                                               m
# org -> sector -> subsector -> division -> section
#
# * Now, if section:costcenter = 1:1, choose costcenter will know section
# * In future, if section:costcenter = 2:1, user will have to choose section


class ResOrg(ResCommon, models.Model):
    _name = 'res.org'
    _description = 'Org'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )
    logo = fields.Binary(
        string='Logo',
    )
    name_print_text = fields.Char(
        string='Print Name',
        size=500,
        translate=True,
    )
    address_print_text = fields.Text(
        string='Print Address',
        translate=True,
        size=1000,
    )
    branch_200 = fields.Text(
        string='Branch 200%',
        translate=True,
        size=1000,
    )

    @api.model
    def _add_name_search_domain(self):
        """ Additiona domain for context's name serach """
        domain = []
        return domain


class ResSector(ResCommon, models.Model):
    _name = 'res.sector'
    _description = 'Sector'
    _rescommon_name_search_list = ['org_id']

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )


class ResSubsector(ResCommon, models.Model):
    _name = 'res.subsector'
    _description = 'Subsector'
    _rescommon_name_search_list = ['org_id', 'sector_id']

    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='sector_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )


class ResDivision(ResCommon, models.Model):
    _name = 'res.division'
    _description = 'Division'
    _rescommon_name_search_list = ['org_id', 'sector_id', 'subsector_id']

    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        required=True,
    )
    sector_id = fields.Many2one(
        'res.sector',
        related='subsector_id.sector_id',
        string='Sector',
        readonly=True,
        required=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='subsector_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )


class ResSection(ResCommon, models.Model):
    _name = 'res.section'
    _description = 'Section'
    _rescommon_name_search_list = ['org_id', 'sector_id',
                                   'subsector_id', 'division_id']

    division_id = fields.Many2one(
        'res.division',
        string='Division',
        required=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        required=True,
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        related='division_id.subsector_id',
        string='Subsector',
        readonly=True,
        store=True,
    )
    sector_id = fields.Many2one(
        'res.sector',
        related='division_id.sector_id',
        string='Sector',
        readonly=True,
        store=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='division_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        required=False,
    )
    fund_ids = fields.Many2many(
        'res.fund',
        'res_fund_section_rel',
        'section_id', 'fund_id',
        string='Funds',
        default=lambda self: self.env.ref('base.fund_nstda'),
    )
    # program_rpt_id = fields.Many2one(
    #     'res.program',
    #     string='Report Program',
    # )
    section_program_id = fields.Many2one(
        'res.section.program',
        string='Section Program',
    )
    internal_charge = fields.Boolean(
        string='Internal Charge',
        default=False,
        help="Service from this section is available as internal charge",
    )

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     if self._context.get('show_all_section', False):
    #         return super(ResCommon, self.sudo()).\
    #             search(args, offset=offset, limit=limit,
    #                    order=order, count=count)
    #   return super(ResSection, self).search(args, offset=offset, limit=limit,
    #                                           order=order, count=count)
    #
    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=80):
    #     if self._context.get('show_all_section', False):
    #         return super(ResCommon, self.sudo()).\
    #             name_search(name=name, args=args,
    #                         operator=operator, limit=limit)
    #     return super(ResSection, self).name_search(name=name, args=args,
    #                                                operator=operator,
    #                                                limit=limit)
    #
    # def read(self, cr, uid, ids, fields=None,
    #          context=None, load='_classic_read'):
    #     if not context:
    #         context = {}
    #     print context
    #     if context.get('show_all_section', False):
    #         uid = 1  # Super User, show all
    #     return super(ResSection, self).read(
    #         cr, uid, ids, fields=fields, context=context, load=load)


class ResSectionView(ResSection, models.Model):
    # View version of section to by pass security rule in some case
    _name = 'res.section.view'
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, "select * from res_section",))


class ResCostcenter(ResCommon, models.Model):
    _name = 'res.costcenter'
    _description = 'Cost Center'

    section_ids = fields.One2many(
        'res.section',
        'costcenter_id',
        string='Sections',
        readonly=True,
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        required=True,
    )


class ResTaxbranch(ResCommon, models.Model):
    _name = 'res.taxbranch'
    _description = 'Tax Branch'
    _order = 'code'

    logo = fields.Binary(
        string='Logo',
    )
    street = fields.Char(
        string='Street',
        size=500,
        translate=True,
    )
    street2 = fields.Char(
        string='Street2',
        size=500,
        translate=True,
    )
    zip = fields.Char(
        string='Zip',
        size=20,
    )
    city = fields.Char(
        string='City',
        translate=True,
        size=100,
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    email = fields.Char(
        string='Email',
        size=100,
    )
    phone = fields.Char(
        string='Phone',
        size=100,
    )
    fax = fields.Char(
        string='Fax',
        size=100,
    )
    website = fields.Char(
        string='website',
        size=100,
    )
    taxid = fields.Char(
        string='Tax ID',
    )
    address_print_text = fields.Text(
        string='Print Address',
        translate=True,
        size=1000,
    )
    address_print_text_receipt = fields.Text(
        string='Print Address (Receipt)',
        translate=True,
        size=1000,
    )
    payment_method_text = fields.Text(
        string='Print Payment Method',
        translate=True,
        size=1000,
    )
    # org_id = fields.Many2one(
    #     'res.org',
    #     string='Org',
    #     required=True,
    # )


# Special new dimension to be shared by Section and Program
class ResSectionProgram(ResCommon, models.Model):
    _name = 'res.section.program'
    _description = 'Section Program'

    section_ids = fields.One2many(
        'res.section',
        'section_program_id',
        string='Sections',
    )
    program_ids = fields.One2many(
        'res.program',
        'section_program_id',
        string='Programs',
    )
