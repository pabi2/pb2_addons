# -*- coding: utf-8 -*-
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

# -------------------------------------------------------------
# THAI
# -------------------------------------------------------------

to_9 = ('ศูนย์', 'หนึ่ง', 'สอง', 'สาม', 'สี่',
        'ห้า', 'หก', 'เจ็ด', 'แปด', 'เก้า')
tens = ('สิบ', 'ยี่สิบ', 'สามสิบ', 'สี่สิบ', 'ห้าสิบ',
        'หกสิบ', 'เจ็ดสิบ', 'แปดสิบ', 'เก้าสิบ')
denom = ('', 'สิบ', 'ร้อย', 'พัน', 'หมื่น', 'แสน', 'ล้าน', 'ล้าน',)


def _convert_nn(val):
    """ convert a value < 10 to Thai.
    """
    if val < 10:
        return to_9[val >= 0 and val or 0]
    for (dcap, dval) in ((k, 10 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + \
                    (to_9[val % 10] == 'หนึ่ง' and 'เอ็ด' or to_9[val % 10])
            return dcap


def _convert_nnn(val):
    """
        convert a value < 1000 to english,
        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.
        This also allows you to get strings in the form
        of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 1000000, val // 1000000)
    if rem > 0:
        word = thai_number(rem) + 'ล้าน'
    if mod > 0:
        word += thai_number(mod)
    return word


def thai_number(val):
    if val < 100:
        return _convert_nn(val)
    if val >= 1000000:
        return _convert_nnn(val)
    for (didx, dval) in ((v - 1, 10 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 10 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l) + denom[didx]
            if r > 0:
                ret = ret + thai_number(r)
            return ret


def amount_to_text_th(number, currency):
    number = '%.2f' % number
    units_name = 'บาท'
    cents_name = 'สตางค์'
    num_list = str(number).split('.')
    start_word = thai_number(int(num_list[0]))
    end_word = thai_number(int(num_list[1]))
    if currency == 'JYP':
        units_name = 'เยน'
        cents_name = 'เซน'
    if currency == 'GBP':
        units_name = 'ปอนด์'
        cents_name = 'เพนนี'
    if currency == 'USD':
        units_name = 'ดอลล่าร์'
        cents_name = 'เซนต์'
    if currency == 'EUR':
        units_name = 'ยูโร'
        cents_name = 'เซนต์'

    if end_word == to_9[0]:
        return ''.join(filter(None, [start_word, units_name,
                                     (start_word or units_name) and
                                     (end_word or cents_name) and 'ถ้วน']))
    else:
        return ''.join(filter(None, [start_word, units_name,
                                     (start_word or units_name) and
                                     (end_word or cents_name) and ' ',
                                     end_word, cents_name]))

# -------------------------------------------------------------
# Generic functions
# -------------------------------------------------------------

_translate_funcs = {'th': amount_to_text_th}


def amount_to_text(nbr, lang='th', currency='baht'):
    """ Converts an integer to its textual representation,
        using the language set in the context if any.
        Example::
            1654: thousands six cent cinquante-quatre.
    """
    if lang not in _translate_funcs:
        _logger.warning(
            _("no translation function found for lang: '%s'"), lang)
        lang = 'th'
    return _translate_funcs[lang](abs(nbr), currency)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
