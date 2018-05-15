# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        res = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            # auto reconcile special account, get all releated move_lines
            v_mlines = voucher.mapped('move_id').mapped('line_id')
            i_mlines = voucher.mapped('line_ids').mapped('invoice_id').\
                mapped('move_id').mapped('line_id')
            tt_mlines = \
                voucher.mapped('recognize_vat_move_id').mapped('line_id')
            mlines = v_mlines + i_mlines + tt_mlines
            mlines.reconcile_special_account()
        return res
