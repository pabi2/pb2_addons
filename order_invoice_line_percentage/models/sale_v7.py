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

from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.osv import fields, osv
import time


class sale_order(osv.osv):

    _inherit = 'sale.order'

    def _invoiced_rate(self, cursor, user, ids, name, arg, context=None):
        """ Overwrite """
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            if sale.invoiced:
                res[sale.id] = 100.0
                continue
            tot = 0.0
            tot_deposit = 0.0
            tot_non_deposit = 0.0
            for invoice in sale.invoice_ids:
                if invoice.state not in ('cancel') and not invoice.is_deposit:
                    # Assume negative line amount to be Advance deduction
                    for line in invoice.invoice_line:
                        tot_non_deposit += line.price_subtotal > 0.0 and \
                            line.price_subtotal or 0.0
            tot = tot_deposit + tot_non_deposit
            if tot:
                res[sale.id] = min(
                    100.0, tot * 100.0 / (sale.amount_untaxed or 1.00))
            else:
                res[sale.id] = 0.0
        return res

    _columns = {
        'invoiced_rate': fields.function(
            _invoiced_rate, string='Invoiced Ratio', type='float'),
    }

    # Overwrite method, just to pass a context
    def action_invoice_create(
            self, cr, uid, ids, grouped=False, states=None,
            date_invoice=False, context=None):
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        # If date was specified, use it as date invoiced, useful when invoices
        # are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context = dict(context or {}, date_invoice=date_invoice)
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and \
                    (partner_currency[o.partner_id.id] != currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different '
                      'currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                # nstda
                # if line.invoiced:
                if line.invoiced and \
                        not context.get('invoice_plan_percent', False):
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            # nstda:
            # created_lines = obj_sale_order_line.invoice_line_create(
            # cr, uid, lines)
            created_lines = obj_sale_order_line.invoice_line_create(
                cr, uid, lines, context=context)
            if created_lines:
                invoices.setdefault(
                    o.partner_invoice_id.id or
                    o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(
                    lambda x, y: x + y, [l for o, l in val], []),
                    context=context)
                invoice_ref = ''
                origin_ref = ''
                for o, l in val:
                    invoice_ref += (o.client_order_ref or o.name) + '|'
                    origin_ref += (o.origin or o.name) + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    cr.execute(
                        "insert into sale_order_invoice_rel "
                        "(order_id,invoice_id) "
                        "values (%s,%s)", (o.id, res))
                    self.invalidate_cache(
                        cr, uid, ['invoice_ids'], [o.id], context=context)
                # remove last '|' in invoice_ref
                if len(invoice_ref) >= 1:
                    invoice_ref = invoice_ref[:-1]
                if len(origin_ref) >= 1:
                    origin_ref = origin_ref[:-1]
                invoice.write(
                    cr, uid, [res],
                    {'origin': origin_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(
                        cr, uid, order, il, context=context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    cr.execute(
                        "insert into sale_order_invoice_rel "
                        "(order_id,invoice_id) values (%s,%s)",
                        (order.id, res))
                    self.invalidate_cache(
                        cr, uid, ['invoice_ids'], [order.id], context=context)
        return res

    def _make_invoice(self, cr, uid, order, lines, context=None):
        """ Overwrite """
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(
            cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)],
            context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(
                cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and \
                    preinv.id not in from_line_invoice_ids:
                # nstda
                if preinv.is_deposit:
                    # --
                    for preline in preinv.invoice_line:
                        inv_line_id = obj_invoice_line.copy(
                            cr, uid, preline.id,
                            {'invoice_id': False,
                             'price_unit': -preline.price_unit})
                        lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        # nstda
        # data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id],
        # inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if context.get('date_invoice', False):
            data = inv_obj.onchange_payment_term_date_invoice(
                cr, uid, [inv_id], inv['payment_term'],
                context.get('date_invoice'))
        else:
            data = inv_obj.onchange_payment_term_date_invoice(
                cr, uid, [inv_id], inv['payment_term'],
                time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        # --
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

    # A complete overwrite method of sale_order_line
    def _fnct_line_invoiced(
            self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        uom_obj = self.pool.get('product.uom')
        for this in self.browse(cr, uid, ids, context=context):
            # kittiu, if product line, we need to calculate carefully
            # TODO: uos case is not covered yet.
            if this.product_id and not this.product_uos:
                oline_qty = uom_obj._compute_qty(
                    cr, uid, this.product_uom.id, this.product_uom_qty,
                    this.product_id.uom_id.id, round=False)
                iline_qty = 0.0
                for iline in this.invoice_lines:
                    if iline.invoice_id.state != 'cancel':
                        if not this.product_uos:  # Normal Case
                            iline_qty += uom_obj._compute_qty(
                                cr, uid, iline.uos_id.id, iline.quantity,
                                iline.product_id and
                                iline.product_id.uom_id.id or False,
                                round=False)
                        else:  # UOS case.
                            iline_qty += iline.quantity / \
                                (iline.product_id.uos_id and
                                 iline.product_id.uos_coeff or 1)
                # Test quantity
                res[this.id] = iline_qty >= oline_qty
            else:
                res[this.id] = this.invoice_lines and \
                    all(iline.invoice_id.state !=
                        'cancel' for iline in this.invoice_lines)
        return res

    # A complete overwrite method. We need it here because it is called from a
    # function field.
    def _order_lines_from_invoice(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve
        # this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT sol.id FROM sale_order_invoice_rel rel JOIN
            sale_order_line sol ON (sol.order_id = rel.order_id)
            WHERE rel.invoice_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()]

    def _prepare_order_line_invoice_line(
            self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=account_id, context=context)
        line_percent = context.get('line_percent', False)
        if line_percent:
            res.update(
                {'quantity':
                 (res.get('quantity') or 0.0) * (line_percent / 100)})
        return res

    _columns = {
        'invoiced': fields.function(
            _fnct_line_invoiced, string='Invoiced', type='boolean',
            store={
                'account.invoice': (_order_lines_from_invoice, ['state'], 10),
                'sale.order.line': (lambda self, cr, uid, ids, ctx=None: ids,
                                    ['invoice_lines'], 10)}),
    }

sale_order_line()
