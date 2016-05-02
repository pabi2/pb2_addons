# -*- coding: utf-8 -*-

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_tax_id = fields.Integer(
        string='Supplier Tax ID',
    )
    supplier_tax_branch = fields.Integer(
        string='Supplier Tax Branch',
    )
