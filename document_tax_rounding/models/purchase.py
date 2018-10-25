# -*- coding: utf-8 -*-
from openerp import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rounding_method = fields.Selection(
        [('round_per_line', 'Round per line'),
         ('round_globally', 'Round globally'), ],
        string='Tax calculation rounding method',
        index=True,
        default=lambda self: self._default_tax_rounding_method()
    )

    @api.model
    def _default_tax_rounding_method(self):
        rounding_tax = self.env["res.company"].search(
            [('id', '=', self.env.user.company_id.id)]
        )
        return rounding_tax.tax_calculation_rounding_method
