# -*- coding: utf-8 -*-

from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True,
    )
