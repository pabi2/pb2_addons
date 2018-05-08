# -*- coding: utf-8 -*-
from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    refer_type = fields.Selection(
        selection_add=[
            ('sale_quotation', 'Sales Quotation'),
            ('purchase_quotation', 'Purchase Quotation'),
            ('sale_order', 'Sales Order'),
            ('purchase_order', 'Purchase Order'),
        ],
    )
