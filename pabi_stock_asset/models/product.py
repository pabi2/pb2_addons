# -*- coding: utf-8 -*-

from openerp import fields, models, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Running Sequence',
    )
