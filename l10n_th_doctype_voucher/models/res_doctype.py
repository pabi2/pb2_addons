# -*- coding: utf-8 -*-
from openerp import models, fields


class ResDoctype(models.Model):
    _inherit = 'res.doctype'

    refer_type = fields.Selection(
        selection_add=[
            ('sale', 'Sales Receipt'),
            ('purchase', 'Purchase Receipt'),
            ('payment', 'Supplier Payment'),
            ('receipt', 'Customer Payment'),
        ],
    )
