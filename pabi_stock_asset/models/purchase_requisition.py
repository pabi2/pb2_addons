# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    is_standard_asset = fields.Boolean(
        string='Standard Asset',
    )
