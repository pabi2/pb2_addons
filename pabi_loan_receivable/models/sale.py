# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    loan_agreement_id = fields.Many2one(
        'loan.customer.agreement',
        string='Loan Agreement',
        readonly=True,
        copy=False,
    )

    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(SaleOrder, self)._prepare_invoice(order, lines)
        if order.loan_agreement_id:
            res.update({
                'origin': order.loan_agreement_id.name,
                'loan_agreement_id': order.loan_agreement_id.id,
            })
        return res
