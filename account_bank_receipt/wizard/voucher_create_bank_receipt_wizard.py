# -*- coding: utf-8 -*-
from openerp import api, models, fields


class VoucherCreateBankReceiptWizard(models.TransientModel):
    _name = "voucher.create.bank.receipt.wizard"

    receipt_date = fields.Date(
        string='Receipt Date',
        required=True,
        default=fields.Date.context_today,
    )

    @api.multi
    def voucher_create_bank_receipt(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        moves = self.env[active_model].browse(active_ids).mapped('move_id')
        moves.create_bank_receipt(self.receipt_date)
        return
