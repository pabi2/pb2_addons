# -*- coding: utf-8 -*-

from openerp import models, api, fields


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
        print self._context
        if order.loan_agreement_id:
            account_id = order.loan_agreement_id.account_receivable_id
            installment = self._context.get('installment')
            res.update({
                'origin': order.loan_agreement_id.name,
                'loan_agreement_id': order.loan_agreement_id.id,
                'account_id': account_id and account_id.id or False,
                'comment':
                u'รับชำระเงินกู้ดอกเบี้ยต่ำ งวดที่ %s' % installment,
            })
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        # Call super
        res = super(SaleOrderLine, self).\
            _prepare_order_line_invoice_line(line, account_id)
        order = line.order_id
        if order.loan_agreement_id:
            installment = self._context.get('installment')
            res.update({
                'section_id': order.loan_agreement_id.section_id.id,
                'name': u'รับชำระเงินกู้ดอกเบี้ยต่ำ งวดที่ %s' % installment,
            })
        return res
