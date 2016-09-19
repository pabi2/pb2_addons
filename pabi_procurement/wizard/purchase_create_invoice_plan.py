# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.tools.float_utils import float_round as round


class PurchaseCreateInvoicePlan(models.TransientModel):
    _inherit = 'purchase.create.invoice.plan'

    @api.one
    def do_create_purchase_invoice_plan(self):
        self._validate_total_amount()
        self.env['purchase.invoice.plan']._validate_installment_date(
            self.installment_ids)
        order = self.env['purchase.order'].browse(self._context['active_id'])
        self._check_invoice_mode(order)
        order.invoice_plan_ids.unlink()
        lines = []
        obj_precision = self.env['decimal.precision']
        prec = obj_precision.precision_get('Account')

        for install in self.installment_ids:
            if install.installment == 0:
                self._check_deposit_account()
                base_amount = order.amount_untaxed
                if install.is_advance_installment:
                    lines.append({
                        'order_id': order.id,
                        'order_line_id': False,
                        'installment': 0,
                        'description': install.description,
                        'is_advance_installment': True,
                        'date_invoice': install.date_invoice,
                        'deposit_percent': install.percent,
                        'deposit_amount': round(install.percent/100 *
                                                base_amount, prec)
                    })
                if install.is_deposit_installment:
                    lines.append({
                        'order_id': order.id,
                        'order_line_id': False,
                        'installment': 0,
                        'description': install.description,
                        'is_deposit_installment': True,
                        'date_invoice': install.date_invoice,
                        'deposit_percent': install.percent,
                        'deposit_amount': round(install.percent/100 *
                                                base_amount, prec)
                    })
            elif install.installment > 0:
                for order_line in order.order_line:
                    if not install.description:
                        desc = order_line.name
                    else:
                        desc = install.description
                    subtotal = order_line.price_subtotal
                    lines.append({
                        'order_id': order.id,
                        'order_line_id': order_line.id,
                        'description': desc,
                        'installment': install.installment,
                        'date_invoice': install.date_invoice,
                        'invoice_percent': install.percent,
                        'invoice_amount': round(install.percent/100 *
                                                subtotal, prec),
                    })
        order.invoice_plan_ids = lines
        order.use_advance = self.use_advance
        order.use_deposit = self.use_deposit
        order.invoice_mode = self.invoice_mode
