
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

from openerp import models, fields, api, _
from openerp.tools.float_utils import float_round as round
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.exceptions import Warning


class sale_invoice_plan(models.Model):
    _name = "sale.invoice.plan"
    _description = "Invoice Plan"
    _order = "order_id,sequence,installment,id"
    
    #dummy = fields.Boolean(string='Dummy', default=False)
    order_id = fields.Many2one('sale.order', string='Order Reference', readonly=True, index=True, ondelete='cascade')
    order_line_id = fields.Many2one('sale.order.line', string='Order Line Reference', index=True, ondelete='cascade', 
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    #order_id = fields.Many2one(related='order_line_id.order_id', store=True)
    sequence = fields.Integer(string='Sequence', default=10, readonly=True, help="Gives the sequence of this line when displaying the invoice plan.")
    installment = fields.Integer(string='Installment', default=1, help="Group of installment. Each group will be an invoice",
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    date_invoice = fields.Date(string='Invoice Date', index=True,
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    #product_id = fields.Many2one('product.product', string='Product', readonly=True,)
    #name = fields.Text(string='Description', readonly=True,)    
    deposit_percent = fields.Float(string='%', digits=(16,10),
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    deposit_amount = fields.Float(string='Advance', digits=dp.get_precision('Account'),
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    invoice_percent = fields.Float(string='%', digits=(16,10),
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    invoice_amount = fields.Float(string='Amount', digits=dp.get_precision('Account'),
            readonly=False, states={'draft': [('readonly', True)], 'proforma': [('readonly', True)], 'proforma2': [('readonly', True)],
                                    'open': [('readonly', True)], 'paid': [('readonly', True)]})
    subtotal = fields.Float(string='Subtotal', digits=dp.get_precision('Account'), readonly=True)
    ref_invoice_id = fields.Many2one('account.invoice', string='Reference Invoice', readonly=True, copy=False)       
    state = fields.Selection([('draft','Draft'),
                                          ('proforma','Pro-forma'),
                                          ('proforma2','Pro-forma'),
                                          ('open','Open'),
                                          ('paid','Paid'),
                                          ('cancel','Cancelled'),], related='ref_invoice_id.state', readonly=True, store=True)

    _sql_constraints = [
        ('name_description_check', 'CHECK(installment >= 0)',
         "Installment must be positive"),
        ('installment_uniq', 'unique(order_id, order_line_id, installment)',
            'Duplicated Installment Sequence!'),
    ]

    @api.one
    @api.onchange('invoice_percent')
    def _onchange_invoice_percent(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        subtotal = self.order_id.price_include and (self.order_line_id.product_uom_qty * self.order_line_id.price_unit) or self.order_line_id.price_subtotal
        self.invoice_amount = round(subtotal and self.invoice_percent/100 * subtotal or 0.0, prec)

    @api.one
    @api.onchange('invoice_amount')
    def _onchange_invoice_amount(self):
        subtotal = self.order_id.price_include and (self.order_line_id.product_uom_qty * self.order_line_id.price_unit) or self.order_line_id.price_subtotal
        new_val = subtotal and (self.invoice_amount / subtotal) * 100 or 0.0
        if round(new_val, 6) != round(self.invoice_percent, 6):
            self.invoice_percent = new_val

    @api.one
    @api.onchange('deposit_percent')
    def _onchange_deposit_percent(self):
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')
        subtotal = self.order_id.price_include and self.order_id.amount_total or self.order_id.amount_untaxed
        self.deposit_amount = round(subtotal and self.deposit_percent/100 * subtotal or 0.0, prec)

    @api.one
    @api.onchange('deposit_amount')
    def _onchange_deposit_amount(self):
        subtotal = self.order_id.price_include and self.order_id.amount_total or self.order_id.amount_untaxed
        new_val = subtotal and (self.deposit_amount / subtotal) * 100 or 0.0
        if round(new_val, 6) != round(self.deposit_percent, 6):
            self.deposit_percent = new_val

    @api.model
    def _validate_installment_date(self, installments):
        dates = []
        for l in installments:
            dates.append(datetime.strptime(l.date_invoice, '%Y-%m-%d')) if l.date_invoice else dates
        sorted_dates = dates[:]
        sorted_dates.sort()
        if dates != sorted_dates:
            raise Warning(_("Invoice date are not in order according to installment sequence"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
