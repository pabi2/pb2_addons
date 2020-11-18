# -*- coding: utf-8 -*-

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standard_price = fields.Float(digits=(12, 4))
