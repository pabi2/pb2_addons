# -*- coding: utf-8 -*-
from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rounding_method = fields.Selection(
        [('round_per_line', 'Round per line'),
         ('round_globally', 'Round globally'), ],
        string='Tax calculation rounding method',
        default=lambda self:
            self.env.user.company_id.tax_calculation_rounding_method
    )
