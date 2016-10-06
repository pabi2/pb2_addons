# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.multi
    def write(self, vals):
        res = super(AccountVoucher, self).write(vals)
        try:
            date_value = vals.get('date_value', False)
            if date_value:
                status = u'Paid'
                status_th = u'จ่ายเงิน'
                comment = u'วันที่เช็ค/โอน %s' % (date_value,)
                for voucher in self:
                    for move_line in voucher.line_ids:
                        exp = move_line.invoice.expense_id
                        if not exp:
                            continue
                        exp.send_comment_to_pabiweb(status, status_th, comment)
        except Exception, e:
            self._cr.rollback()
            raise ValidationError(e)
        return res
