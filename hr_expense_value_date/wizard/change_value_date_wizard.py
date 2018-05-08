# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ChangeDateValue(models.TransientModel):
    _name = 'change.date.value'

    date_value = fields.Date(
        string='Value Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    reason = fields.Char(
        string="Reason",
        required=True,
    )

    @api.multi
    def action_change_date_value(self):
        voucher_ids = self._context.get('active_ids', [])
        voucher_ids = self.env['account.voucher'].browse(voucher_ids)
        for voucher in voucher_ids:
            if voucher.type == 'payment':
                if voucher.state in ('draft', 'cancel'):
                    raise ValidationError(_('You can not change Value Date \
                        for new or cancelled payments.'))
                voucher.date_value = self.date_value
                for line in voucher.line_ids:
                    invoice = line.move_line_id.invoice
                    if invoice:
                        self.env['date.value.history'].create({
                            'voucher_id': voucher.id,
                            'invoice_id': invoice.id,
                            'expense_id': invoice.expense_id.id,
                            'date_value': self.date_value,
                            'amount': line.amount,
                            'user_id': self.env.user.id,
                            'date': fields.Date.context_today(voucher),
                            'reason': self.reason,
                        })
        return True
