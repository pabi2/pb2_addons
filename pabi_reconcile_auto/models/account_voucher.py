# -*- coding: utf-8 -*-
from openerp import models, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def proforma_voucher(self):
        """ Payment to reconcile invoice is a natural case,
        auto_reconcile_id is not required """
        res = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            # auto reconcile special account, get all releated move_lines
            v_mlines = voucher.mapped('move_id.line_id')
            i_mlines = voucher.mapped('line_ids.invoice_id.move_id.line_id')
            tt_mlines = \
                voucher.mapped('recognize_vat_move_id.line_id')
            mlines = v_mlines | i_mlines | tt_mlines
            mlines.reconcile_special_account()
        return res
