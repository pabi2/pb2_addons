# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.l10n_th_amount_text.amount_to_text_th \
    import amount_to_text_th


class AmountToWord(object):

    def _get_amount_total(self, obj):
        amount_total = 0.0
        # Order, Invoice
        if obj._name in ('account.invoice', 'sale.order', 'purchase.order'):
            amount_total = obj.amount_total
        elif obj._name == 'account.voucher':
            for cr_line in obj.line_cr_ids:
                amount_total += cr_line.amount
            for dr_line in obj.line_dr_ids:
                amount_total -= dr_line.amount
            amount_total = abs(amount_total)
        return amount_total

    def _amount_to_word_en(self, cursor, user, ids, name, arg, context=None):
        res = {}
        minus = False
        amount_text = ''
        for obj in self.browse(cursor, user, ids, context=context):
            a = 'Baht'
            b = 'Satang'
            if obj.currency_id.name == 'JPY':
                a = 'Yen'
                b = 'Sen'
            if obj.currency_id.name == 'GBP':
                a = 'Pound'
                b = 'Penny'
            if obj.currency_id.name == 'USD':
                a = 'Dollar'
                b = 'Cent'
            if obj.currency_id.name == 'EUR':
                a = 'Euro'
                b = 'Cent'
            if obj.currency_id.name == 'SGD':
                a = 'Dollar'
                b = 'Cent'
            if obj.currency_id.name == 'CHF':
                a = 'Franc'
                b = 'Cent'
            if obj.currency_id.name == 'AUD':
                a = 'Dollar'
                b = 'Cent'
            if obj.currency_id.name == 'CNY':
                a = 'Yuan'
                b = ' '
            amount_total = self._get_amount_total(obj)
            if amount_total < 0:
                minus = True
                amount_total = -amount_total
            amount_text = amount_to_text(
                amount_total, 'en', a).replace(
                    'and Zero Cent', 'Only').replace(
                        'Cent', b).replace('Cents', b)
            final_amount_text = (minus and 'Minus ' +
                                 amount_text or amount_text).lower()
            res[obj.id] = final_amount_text[:1].upper() + final_amount_text[1:]
        return res

    def _amount_to_word_th(self, cursor, user, ids, name, arg, context=None):
        res = {}
        minus = False
        amount_text = ''
        for obj in self.browse(cursor, user, ids, context=context):
            amount_total = self._get_amount_total(obj)
            if amount_total < 0:
                minus = True
                amount_total = -amount_total
            amount_text = amount_to_text_th(amount_total, obj.currency_id.name)
            res[obj.id] = minus and 'ลบ' + amount_text or amount_text

        return res

    def copy(self, cr, uid, id, default, context=None):
        if default is None:
            default = {}
        default.update({'amount_total_text_en': False,
                        'amount_total_text_th': False})
        return super(AmountToWord, self).copy(cr, uid, id,
                                              default, context=context)


class AccountInvoice(AmountToWord, osv.osv):
    _inherit = 'account.invoice'

    def _amount_total_text_en(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_en(
            cursor, user, ids, name, arg, context=context)

    def _amount_total_text_th(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_th(cursor, user, ids, name,
                                       arg, context=context)

    _columns = {
        'amount_total_text_en': fields.function(
            _amount_total_text_en, string='Amount Total (EN)', type='char',
            store={'account.invoice':
                   (lambda self, cr, uid, ids, c={}:
                    ids, ['amount_total'], 1000),
                   }),
        'amount_total_text_th': fields.function(
            _amount_total_text_th, string='Amount Total (TH)', type='char',
            store={'account.invoice':
                   (lambda self, cr, uid, ids, c={}:
                    ids, ['amount_total'], 1000),
                   }),
    }


class AccountVoucher(AmountToWord, osv.osv):
    _inherit = 'account.voucher'

    def _amount_total_text_en(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_en(cursor, user, ids, name,
                                       arg, context=context)

    def _amount_total_text_th(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_th(cursor, user, ids, name,
                                       arg, context=context)

    _columns = {
        'amount_total_text_en': fields.function(
            _amount_total_text_en, string='Amount Total (EN)', type='char',
            store={'account.voucher':
                   (lambda self, cr, uid, ids, c={}:
                    ids, ['amount'], 1000),
                   }),
        'amount_total_text_th': fields.function(
            _amount_total_text_th, string='Amount Total (TH)', type='char',
            store={'account.voucher':
                   (lambda self, cr, uid, ids, c={}:
                    ids, ['amount'], 1000),
                   }),
    }


class SaleOrder(AmountToWord, osv.osv):
    _inherit = 'sale.order'

    def _amount_total_text_en(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_en(cursor, user, ids, name,
                                       arg, context=context)

    def _amount_total_text_th(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_th(cursor, user, ids, name,
                                       arg, context=context)

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids,
                                                            context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_total_text_en': fields.function(
            _amount_total_text_en, string='Amount Total (EN)', type='char',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 1000),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty'], 1000),
            }),
        'amount_total_text_th': fields.function(
            _amount_total_text_th, string='Amount Total (TH)', type='char',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}:
                               ids, ['order_line'], 1000),
                'sale.order.line': (_get_order,
                                    ['price_unit', 'tax_id',
                                     'discount', 'product_uom_qty'], 1000),
            }),
    }


class PurchaseOrder(AmountToWord, osv.osv):
    _inherit = 'purchase.order'

    def _amount_total_text_en(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_en(cursor, user, ids, name,
                                       arg, context=context)

    def _amount_total_text_th(
            self, cursor, user, ids, name, arg, context=None):
        return self._amount_to_word_th(cursor, user, ids, name,
                                       arg, context=context)

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').\
                browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_total_text_en': fields.function(
            _amount_total_text_en, string='Amount Total (EN)', type='char',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}:
                                   ids, ['order_line', 'currency_id'], 1000),
                'purchase.order.line': (_get_order,
                                        ['price_unit', 'taxes_id',
                                         'product_qty'], 1000),
            }),
        'amount_total_text_th': fields.function(
            _amount_total_text_th, string='Amount Total (TH)', type='char',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}:
                                   ids, ['order_line'], 1000),
                'purchase.order.line': (_get_order,
                                        ['price_unit', 'taxes_id',
                                         'product_qty'], 1000),
            }),
    }
