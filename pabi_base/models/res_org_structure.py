# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp.addons.pabi_base.models.res_common import ResCommon

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
        translate=True,
    )
    address_print_text = fields.Text(
        string='Print Address',
        translate=True,
    )
    branch_200 = fields.Text(
        string='Branch 200%',
        translate=True,
    )


class ResSector(ResCommon, models.Model):
    _name = 'res.sector'
    _description = 'Sector'

    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )


class ResSubsector(ResCommon, models.Model):
    _name = 'res.subsector'
    _description = 'Subsector'

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
    )


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
        required=False,
    )


class ResTaxbranch(ResCommon, models.Model):
    _name = 'res.taxbranch'
    _description = 'Tax Branch'

    street = fields.Char(
        string='Street',
        translate=True,
    )
    street2 = fields.Char(
        string='Street2',
        translate=True,
    )
    zip = fields.Char(
        string='Zip',
    )
    city = fields.Char(
        string='City',
        translate=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    email = fields.Char(
        string='Email',
    )
    phone = fields.Char(
        string='Phone',
    )
    fax = fields.Char(
        string='Fax',
    )
    website = fields.Char(
        string='website',
    )
    taxid = fields.Char(
        string='Tax ID',
    )
    address_print_text = fields.Text(
        string='Print Address',
        translate=True,
    )
    address_print_text_receipt = fields.Text(
        string='Print Address (Receipt)',
        translate=True,
    )
    payment_method_text = fields.Text(
        string='Print Payment Method',
        translate=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )
