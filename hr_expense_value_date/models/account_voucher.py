# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    date_value_history_ids = fields.One2many(
        'date.value.history',
        'voucher_id',
        string='Value Date History',
        readonly=True,
    )

    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            if voucher.type == 'payment':
                for line in voucher.line_ids:
                    invoice = line.move_line_id.invoice
                    if invoice and invoice.expense_id:
                        self.env['date.value.history'].create({
                            'voucher_id': voucher.id,
                            'invoice_id': invoice.id,
                            'expense_id': invoice.expense_id.id,
                            'date_value': voucher.date_value,
                            'amount': line.amount,
                            'user_id': self.env.user.id,
                            'date': fields.Date.context_today(voucher),
                        })
        return result
