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
            amount_total = obj.amount
        return amount_total


class SaleOrder(AmountToWordExt, osv.osv):
    _inherit = 'sale.order'


class PurchaseOrder(AmountToWordExt, osv.osv):
    _inherit = 'purchase.order'


class AccountInvoice(AmountToWordExt, osv.osv):
    _inherit = 'account.invoice'


class AccountVoucher(AmountToWordExt, osv.osv):
    _inherit = 'account.voucher'
