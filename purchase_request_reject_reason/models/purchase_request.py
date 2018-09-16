# -*- coding: utf-8 -*-

from openerp import fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    reject_reason_txt = fields.Char(
        string="Rejected Reason",
        readonly=True,
        size=500,
    )
