# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import _
from openerp.exceptions import ValidationError


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _anglo_saxon_purchase_move_lines(self, cr, uid, i_line, res, context=None):
        """Return the additional move lines for purchase invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id.id
        if i_line.product_id and i_line.product_id.valuation == 'real_time':
            if i_line.product_id.type != 'service':
                # get the price difference account at the product
                acc = i_line.product_id.property_account_creditor_price_difference and i_line.product_id.property_account_creditor_price_difference.id
                if not acc:
                    # if not found on the product get the price difference account at the category
                    acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ and i_line.product_id.categ_id.property_account_creditor_price_difference_categ.id
                a = None

                # oa will be the stock input account
                # first check the product, if empty check the category
                oa = i_line.product_id.property_stock_account_input and i_line.product_id.property_stock_account_input.id
                if not oa:
                    oa = i_line.product_id.categ_id.property_stock_account_input_categ and i_line.product_id.categ_id.property_stock_account_input_categ.id
                if oa:
                    # get the fiscal position
                    fpos = i_line.invoice_id.fiscal_position or False
                    a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, oa)
                diff_res = []
                # calculate and write down the possible price difference between invoice price and product price
                for line in res:
                    if line.get('invl_id', 0) == i_line.id and a == line['account_id']:
                        uom = i_line.product_id.uos_id or i_line.product_id.uom_id
                        valuation_price_unit = self.pool.get('product.uom')._compute_price(cr, uid, uom.id, i_line.product_id.standard_price, i_line.uos_id.id)
                        if i_line.product_id.cost_method != 'standard' and i_line.purchase_line_id:
                            #for average/fifo/lifo costing method, fetch real cost price from incomming moves
                            stock_move_obj = self.pool.get('stock.move')
                            valuation_stock_move = stock_move_obj.search(cr, uid, [('purchase_line_id', '=', i_line.purchase_line_id.id)], limit=1, context=context)
                            if valuation_stock_move:
                                valuation_price_unit = stock_move_obj.browse(cr, uid, valuation_stock_move[0], context=context).price_unit
                        if inv.currency_id.id != company_currency:
                            valuation_price_unit = self.pool.get('res.currency').compute(cr, uid, company_currency, inv.currency_id.id, valuation_price_unit, context={'date': inv.date_invoice})
                        if valuation_price_unit != i_line.price_unit and line['price_unit'] == i_line.price_unit and acc:
                            raise ValidationError(_("This document has price diff.Please Contact Support Team."))
                return diff_res
        return []
