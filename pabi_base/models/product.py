# -*- coding: utf-8 -*-
from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = ''  # Remove name sorting for performance
    
    name = fields.Char(track_visibility='onchange',)
    sale_ok = fields.Boolean(track_visibility='onchange',)
    hr_expense_ok = fields.Boolean(track_visibility='onchange',)
    purchase_ok = fields.Boolean(track_visibility='onchange',)
    type = fields.Selection(track_visibility='onchange',)
    uom_id = fields.Many2one(track_visibility='onchange',)
    categ_id = fields.Many2one(track_visibility='onchange',)
    taxes_id =fields.Many2many(track_visibility='onchange',)
    legacy_ref = fields.Char(
        string='Legacy Ref.',
        readonly=False,
        size=10,
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'default_code'  # Remove name sorting for performance improve
    
    product_tmpl_id = fields.Many2one(track_visibility='onchange',)
    lst_price = fields.Float(track_visibility='onchange',)
    active = fields.Boolean(track_visibility='onchange',)
    ean13 = fields.Char(track_visibility='onchange',)
    default_code = fields.Char(track_visibility='onchange',)
    
    
    def _check_ean_key(self, cr, uid, ids, context=None):
        """ By pass checking """
        return True

    _constraints = [(
        _check_ean_key, 'N/A', ['ean13'])]


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _order = 'parent_id, name'  # Better sorting (may affect some performance)
