# -*- coding: utf-8 -*-
from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    operating_unit_id = fields.Many2one(
        required=True,
    )
