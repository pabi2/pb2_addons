# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    operating_unit_id = fields.Many2one(
        required=True,
        domain=lambda self: self.env['operating.unit']._ou_domain(),
    )
    requesting_operating_unit_id = fields.Many2one(
        required=True,
        domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    operating_unit_id = fields.Many2one(required=False)
