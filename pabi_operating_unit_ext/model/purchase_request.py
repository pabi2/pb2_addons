# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
