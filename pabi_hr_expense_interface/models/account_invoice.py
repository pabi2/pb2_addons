# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _send_comment_diff_reason(self):
        try:
            for invoice in self:
                if invoice.diff_expense_amount_flag == -1:
                    exp = invoice.expense_id
                    amount = invoice.amount_expense_request
                    amount_adj = invoice.diff_expense_amount_adjusted
                    reason = invoice.diff_expense_amount_reason
                    status = u'Invoice Confimed'
                    status_th = u'ยืนยันใบวางบิล'
                    comment = u'ปรับปรุงยอดเงิน %s → %s เหตุผล: %s' % \
                        ('{:,.2f}'.format(amount),
                         '{:,.2f}'.format(amount_adj),
                         reason)
                    exp.send_comment_to_pabiweb(status, status_th, comment)
        except Exception, e:
            self._cr.rollback()
            raise ValidationError(str(e))
        return

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        self._send_comment_diff_reason()
        return result
