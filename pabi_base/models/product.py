# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sap_code = fields.Char(
        string='SAP Code',
        size=10,
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'default_code'  # Remove name sorting for performance improve


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _order = 'parent_id, name'  # Better sorting (may affect some performance)
