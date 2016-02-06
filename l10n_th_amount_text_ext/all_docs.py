# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

from openerp.osv import osv
from openerp.addons.l10n_th_amount_text.all_docs import AmountToWord


class AmountToWordExt(AmountToWord):

    def _get_amount_total(self, obj):
        """ Override """
        amount_total = 0.0
        if obj._name in ('account.invoice', 'sale.order'): # Order, Invoice
            amount_total = obj.amount_total
        elif obj._name == 'account.voucher':
            for cr_line in obj.line_cr_ids:
                amount_total += (cr_line.amount + cr_line.amount_retention + cr_line.amount_wht)
            for dr_line in obj.line_dr_ids:
                amount_total -= (dr_line.amount + dr_line.amount_retention + dr_line.amount_wht)
            amount_total = abs(amount_total)
        return amount_total


class sale_order(AmountToWordExt, osv.osv):

    _inherit = 'sale.order'


class account_invoice(AmountToWordExt, osv.osv):

    _inherit = 'account.invoice'


class account_voucher(AmountToWordExt, osv.osv):

    _inherit = 'account.voucher'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
