# -*- coding: utf-8 -*-
from openerp import fields, models


class WkfConfigPurchaseUnit(models.Model):
    _name = 'wkf.config.purchase.unit'
    _description = 'Purchasing Unit'

    name = fields.Char(
        string='Name',
        required=True,
        size=500,
    )
    description = fields.Text(
        string='Description',
        size=1000,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
    )
    doctype_id = fields.Many2one(
        'wkf.config.doctype',
        domain="[('module', 'in', ('purchase', 'purchase_pd'))]",
        string='Document Type',
        required=True,
    )
    responsible_ids = fields.One2many(
        'wkf.config.purchase.unit.responsible',
        'purchasing_unit_id',
        string='Responsible',
        copy=True,
    )
    section_ids = fields.Many2many(
        'res.section',
        'purchasingunit_section_rel',
        'purchasing_unit_id',
        'section_id',
        string='Section',
    )


class WkfConfigPurchaseUnitResponsible(models.Model):
    _name = 'wkf.config.purchase.unit.responsible'
    _description = 'Purchasing Unit Responsible'

    purchasing_unit_id = fields.Many2one(
        'wkf.config.purchase.unit',
        string='Purchasing Unit',
        required=True,
        ondelete='cascade',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    level = fields.Selection([
        ('L01', "L01"),
        ('L02', "L02"), ],
        string='Level',
        required=True,
    )
