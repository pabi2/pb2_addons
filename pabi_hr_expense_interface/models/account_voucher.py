# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.multi
    def _send_comment_onchange_date_value(self):
        try:
            for voucher in self:
                if not voucher.date_value:
                    continue
                status = u'Payment Approved'
                status_th = u'อนุมัติจ่าย'
                comment = u'วันที่เช็ค/โอน %s' % (voucher.date_value,)
                for line in voucher.line_ids:
                    exp = line.move_line_id.invoice.expense_id
                    if not exp:
                        continue
                    exp.send_comment_to_pabiweb(status,
                                                status_th,
                                                comment)
        except Exception, e:
            self._cr.rollback()
            raise ValidationError(str(e))
        return

    @api.multi
    def proforma_voucher(self):
        res = super(AccountVoucher, self).proforma_voucher()
        if self.id not in (67427,67428,67423):
            self._send_comment_onchange_date_value()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountVoucher, self).write(vals)
        if vals.get('date_value', False):
            self._send_comment_onchange_date_value()
        return res
