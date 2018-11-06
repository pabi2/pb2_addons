# -*- coding: utf-8 -*-
from openerp import api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    round_total = fields.Boolean(
        default=False,
    )

    @api.multi
    @api.depends('round_total', 'line_ids.price_subtotal',
                 'line_ids.tax_ids')
    def _compute_amount(self):
        super(PurchaseRequisition, self)._compute_amount()
        for requisition in self:
            if requisition.round_total:
                requisition.amount_total = round(
                    requisition.amount_total, 0)
                requisition.amount_tax = requisition.amount_total - \
                    requisition.amount_untaxed
        return True
