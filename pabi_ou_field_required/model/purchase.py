# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    operating_unit_id = fields.Many2one(required=True)
    requesting_operating_unit_id = fields.Many2one(required=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    operating_unit_id = fields.Many2one(required=True)
