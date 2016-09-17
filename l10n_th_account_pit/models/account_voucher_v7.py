# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class account_voucher(osv.osv):

    _inherit = 'account.voucher'

    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        res = super(account_voucher, self).\
            _get_writeoff_amount(cr, uid, ids, name, args, context=context)
        vouchers = self.browse(cr, uid, ids, context=context)
        for voucher in vouchers:
            amount_wht = sum([x.amount_wht for x in voucher.pit_line])
            res[voucher.id] -= amount_wht
        return res

    _columns = {
        'writeoff_amount': fields.function(
            _get_writeoff_amount,
            string='Difference Amount',
            type='float', readonly=True,
            help="""Computed as the difference between the amount stated in the
                   voucher and the sum of allocation on the voucher lines."""),
    }
