# -*- coding: utf-8 -*-
from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_term = fields.Many2one(
        'account.payment.term',
        domain=[('revenue', '=', True)],
    )
