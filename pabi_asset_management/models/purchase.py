# -*- coding: utf-8 -*-
from openerp import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    parent_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Prototype',
        domain="[('parent_id', '=', False),"
        "('type', '=', 'view'),"
        "('project_id', '=', project_id)]",
        help="The project prototype the receiving asset will belong to.",
    )
