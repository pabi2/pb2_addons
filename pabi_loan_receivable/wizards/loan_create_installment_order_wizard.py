# -*- coding: utf-8 -*-
import ast
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from openerp import api, models, fields


class LoanCreateInstallmentOrderWizard(models.TransientModel):
    _name = "loan.create.installment.order.wizard"

    date_order = fields.Date(
        string='First Installment Due date',
        required=True,
        help="The due date must comply with Payment Due type"
    )
    amount = fields.Float(
        string='Amount',
        readonly=True,
    )
    installment = fields.Integer(
        string='Number of Installment',
        readonly=True,
    )
    install_amount = fields.Float(
        string='Amount/Installment',
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(LoanCreateInstallmentOrderWizard,
                    self).default_get(field_list)
        Loan = self.env['loan.customer.agreement']
        loan = Loan.browse(self._context.get('active_id'))
        first_date_due = self._compute_first_date_due(loan)
        res['date_order'] = first_date_due
        res['amount'] = loan.amount_receivable
        res['installment'] = loan.installment
        res['install_amount'] = loan.installment and \
            loan.amount_receivable / loan.installment
        return res

    @api.model
    def _compute_first_date_due(self, loan):
        date_begin = datetime.strptime(loan.date_begin, '%Y-%m-%d')
        first_date = date(date_begin.year, date_begin.month, 1)
        date_return = False
        if loan.monthly_due_type == 'first':
            date_return = first_date + relativedelta(months=1)
        elif loan.monthly_due_type == 'last':
            months = relativedelta(months=2)
            days = relativedelta(days=1)
            date_return = first_date + months - days
        elif loan.monthly_due_type == 'specific':
            date_return = first_date + relativedelta(months=1)
            date_return = date(date_return.year, date_return.month,
                               loan.date_specified)
        return date_return and date_return.strftime('%Y-%m-%d')

    @api.multi
    def action_create_installment_order(self):
        self.ensure_one()
        Loan = self.env['loan.customer.agreement']
        loan = Loan.browse(self._context.get('active_id', False))
        order = loan.create_installment_order(self.date_order)
        return self.open_invoice_plan_wizard(order.id)

    @api.multi
    def open_invoice_plan_wizard(self, order_id):
        self.ensure_one()
        action = self.env.ref(
            'sale_invoice_plan.action_sale_create_invoice_plan')
        result = action.read()[0]
        ctx = ast.literal_eval(result['context'])
        ctx.update({'loan_agreement_id': self._context.get('active_id', False),
                    'active_id': order_id,
                    'active_ids': [order_id],
                    'active_model': 'sale.order',
                    'default_num_installment': self.installment,
                    'loan_install_amount': self.install_amount,
                    'readonly_num_installment': True,
                    'hide_invoice_plan_detail': True,
                    })
        result['context'] = ctx
        return result
