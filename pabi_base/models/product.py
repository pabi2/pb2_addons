# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = ''  # Remove name sorting for performance

    legacy_ref = fields.Char(
        string='Legacy Ref.',
        readonly=False,
        size=10,
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'default_code'  # Remove name sorting for performance improve

    def _check_ean_key(self, cr, uid, ids, context=None):
        """ By pass checking """
        return True

    _constraints = [(
        _check_ean_key, 'N/A', ['ean13'])]


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _order = 'parent_id, name'  # Better sorting (may affect some performance)
