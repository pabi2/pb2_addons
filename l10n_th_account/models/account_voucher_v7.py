# -*- coding: utf-8 -*-
#
#    Author: Kitti Upariphutthiphong
#    Copyright 2014-2015 Ecosoft Co., Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


from openerp.osv import fields, osv


class account_voucher(osv.osv):

    _inherit = 'account.voucher'

    # This is a complete overwrite method
    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        currency_obj = self.pool.get('res.currency')
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            debit = credit = 0.0
            sign = voucher.type == 'payment' and -1 or 1
            for l in voucher.line_dr_ids:
                debit += l.amount + l.amount_wht + l.amount_retention  # WHT
            for l in voucher.line_cr_ids:
                credit += l.amount + l.amount_wht + l.amount_retention  # WHT
            currency = voucher.currency_id or voucher.company_id.currency_id
            res[voucher.id] = currency_obj.round(cr, uid, currency,
                                                 voucher.amount -
                                                 sign * (credit - debit))
        return res

    _columns = {
        'writeoff_amount': fields.function(
            _get_writeoff_amount,
            string='Difference Amount',
            type='float', readonly=True,
            help="""Computed as the difference between the amount stated in the
                   voucher and the sum of allocation on the voucher lines."""),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
