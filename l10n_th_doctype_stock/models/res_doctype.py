# -*- coding: utf-8 -*-
from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    refer_type = fields.Selection(
        selection_add=[
            ('incoming_shipment', 'Incoming Shipment'),
            ('delivery_order', 'Delivery Order'),
            ('internal_transfer', 'Internal Transfer'),
        ],
    )
