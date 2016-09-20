# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    delivery_penalty_product_id = fields.Many2one(
        'product.product',
        string='Delivery Penalty Product',
        related="company_id.delivery_penalty_product_id",
    )
