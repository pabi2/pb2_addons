# -*- coding: utf-8 -*-
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_tax_ids = fields.Many2many(
        'account.tax',
        'customer_tax_rel',
        'partner_id', 'tax_id',
        string='Customer Default Taxes',
        domain=[('parent_id', '=', False),
                ('type_tax_use', 'in', ['sale', 'all'])],
    )
    supplier_tax_ids = fields.Many2many(
        'account.tax',
        'supplier_tax_rel',
        'partner_id', 'tax_id',
        string='Supplier Default Taxes',
        domain=[('parent_id', '=', False),
                ('type_tax_use', 'in', ['purchase', 'all'])],
    )
