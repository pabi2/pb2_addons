# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    operating_unit_id = fields.Many2one(required=True)


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    operating_unit_id = fields.Many2one(required=True)
