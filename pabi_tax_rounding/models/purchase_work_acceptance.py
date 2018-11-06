# -*- coding: utf-8 -*-
from openerp import models, fields, api


class PurchaseWorkAcceptance(models.Model):
    _inherit = 'purchase.work.acceptance'

    round_total = fields.Boolean(
        default=False,
    )

    @api.multi
    @api.depends('round_total', 'acceptance_line_ids.price_subtotal',
                 'acceptance_line_ids.tax_ids')
    def _compute_amount(self):
        super(PurchaseWorkAcceptance, self)._compute_amount()
        for order in self:
            if order.round_total:
                order.amount_total = round(order.amount_total, 0)
                order.amount_tax = order.amount_total - order.amount_untaxed
        return True
