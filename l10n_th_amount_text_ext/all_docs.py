# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.addons.l10n_th_amount_text.all_docs import AmountToWord


class AmountToWordExt(AmountToWord):

    def _get_amount_total(self, obj):
        """ Overwrite (ok) """
        amount_total = 0.0
        # Order, Invoice
        if obj._name in ('account.invoice', 'sale.order', 'purchase.order'):
            amount_total = obj.amount_total
        elif obj._name == 'account.voucher':
            for cr_line in obj.line_cr_ids:
                amount_total += (cr_line.amount +
                                 cr_line.amount_retention +
                                 cr_line.amount_wht)
            for dr_line in obj.line_dr_ids:
                amount_total -= (dr_line.amount +
                                 dr_line.amount_retention +
                                 dr_line.amount_wht)
            amount_total = abs(amount_total)
        return amount_total


class sale_order(AmountToWordExt, osv.osv):

    _inherit = 'sale.order'


class purchase_order(AmountToWordExt, osv.osv):

    _inherit = 'purchase.order'


class account_invoice(AmountToWordExt, osv.osv):

    _inherit = 'account.invoice'


class account_voucher(AmountToWordExt, osv.osv):

    _inherit = 'account.voucher'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
