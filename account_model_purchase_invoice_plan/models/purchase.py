# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_fin_lease = fields.Boolean(
        string='Financial Lease',
        default=False,
        help='If checked, this Invoice Plan will not participate in recurring',
    )
