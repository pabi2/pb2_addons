# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_mode = fields.Selection(
        readonly=False,
    )
