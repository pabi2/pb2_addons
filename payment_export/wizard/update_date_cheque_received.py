# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class UpdateDateChequeReceived(models.TransientModel):
    _name = "update.date.cheque.received"

    date_cheque_received = fields.Date(
        string='Cheque Received Date',
        required=True,
    )

    @api.multi
    def action_update_date_cheque_received(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        records = self.env[active_model].browse(active_ids)
        # Payment type must be cheque
        vouchers = records.filtered(
            lambda l: l.payment_type != 'cheque' and l.number).mapped('number')
        print vouchers
        if vouchers:
            raise ValidationError(
                _('Following payments is not of type "Cheque"\n%s') %
                ', '.join(vouchers))
        records.write({'date_cheque_received': self.date_cheque_received})
