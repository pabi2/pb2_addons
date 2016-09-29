# -*- coding: utf-8 -*-

from openerp import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Running Sequence',
    )


class ProductCategory(models.Model):
    _inherit = 'product.category'

    asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Asset Category',
    )
