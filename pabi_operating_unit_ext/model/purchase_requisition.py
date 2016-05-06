# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    operating_unit_id = fields.Many2one(
        required=True,
        domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    operating_unit_id = fields.Many2one(required=False)
