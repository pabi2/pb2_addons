# -*- coding: utf-8 -*-
from openerp import api, models, fields


class VoucherCreateBankReceiptWizard(models.TransientModel):
    _name = "voucher.create.bank.receipt.wizard"

    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        required=True,
    )

    @api.multi
    def voucher_create_bank_receipt(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        moves = self.env[active_model].browse(active_ids).mapped('move_id')
        bank_receipt_id = moves.create_bank_receipt(self.partner_bank_id.id)
