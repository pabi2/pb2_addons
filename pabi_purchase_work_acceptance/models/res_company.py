# -*- coding: utf-8 -*-
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    delivery_penalty_product_id = fields.Many2one(
        'product.product',
        string='Delivery Penalty Product',
    )
