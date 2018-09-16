# -*- coding: utf-8 -*-

from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_done_reason = fields.Text(
        string="Force Done Reason",
        size=1000,
    )
