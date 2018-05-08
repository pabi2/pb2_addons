# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
