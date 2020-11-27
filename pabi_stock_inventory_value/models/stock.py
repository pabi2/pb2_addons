# -*- coding: utf-8 -*-

from openerp import models, fields


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    inventory_value = fields.Float(digits=(16, 4))
