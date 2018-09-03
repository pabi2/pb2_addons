# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    request_id = fields.Many2one(
        'purchase.request',
        readonly=False,
    )
