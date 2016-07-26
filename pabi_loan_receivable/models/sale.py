# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(SaleOrderLine, self).\
            _prepare_order_line_invoice_line(line, account_id)
        # For loan agreement invoice plan, add installment #
        if line.order_id.loan_agreement_id:
            if res.get('name', False):
                res['name'] += (_(' / Installment %s') %
                                (self._context.get('installment'),))
        return res
