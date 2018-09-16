
# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, models


class sale_create_invoice_plan(models.TransientModel):
    _inherit = 'sale.create.invoice.plan'

    @api.onchange('use_deposit', 'num_installment')
    def _onchange_plan(self):
        installments = super(sale_create_invoice_plan, self)._onchange_plan()
        # Case Loan Agreement
        loan_agreement_id = self._context.get('loan_agreement_id', False)
        install_amount = self._context.get('loan_install_amount', False)
        if not loan_agreement_id:
            return installments

        # Auto fill installment, based on
        # 1) first date 2) amount 3) num_installment
        order_id = self._context['active_id']
        order = self.env['sale.order'].browse(order_id)
        first_date = datetime.strptime(order.date_order,
                                       '%Y-%m-%d %H:%M:%S').date()
        avg_amount = install_amount or \
            (self.num_installment and
             (self.order_amount / self.num_installment) or 0.0)

        i = 0
        accum_amount = 0.0
        accum_percent = 0.0
        num_install = len(installments)
        for install in installments:
            next_date = first_date + relativedelta(months=i)
            install.date_invoice = next_date.strftime('%Y-%m-%d')
            remain_amount = self.order_amount - accum_amount
            if i == num_install or remain_amount < avg_amount:  # Final round
                install.amount = remain_amount
                install.percent = 100.0 - accum_percent
            else:
                # Decimal will interact with each other.
                install.amount = avg_amount
                install.percent = (install.amount / self.order_amount) * 100.0
            accum_amount += install.amount
            accum_percent += install.percent
            i += 1
        return installments
