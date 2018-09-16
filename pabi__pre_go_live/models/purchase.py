# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_mode = fields.Selection(
        readonly=False,
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    docline_seq = fields.Integer(
        readonly=False,
    )
