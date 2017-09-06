# -*- coding: utf-8 -*-
from openerp import api, models, fields


class VoucherCreateBankPaymentWizard(models.TransientModel):
    _name = "voucher.create.bank.payment.wizard"

    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.context_today,
    )

    @api.multi
    def voucher_create_bank_payment(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        moves = self.env[active_model].browse(active_ids).mapped('move_id')
        bank_payment_id = moves.create_bank_payment(self.payment_date)
        action = self.env.ref('account_bank_payment.action_bank_payment_tree')
        result = action.read()[0]
        result['domain'] = [('id', '=', bank_payment_id)]
        return result
