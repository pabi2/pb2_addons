# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        compute='_compute_bank_cheque_lot',
    )
    is_cheque_lot = fields.Boolean(
        string='Is Cheque Lot Available',
        compute='_compute_bank_cheque_lot',
    )
    cheque_lot_id = fields.Many2one(
        'cheque.lot',
        string='Cheque Lot',
        domain="[('bank_id', '=', bank_id), ('state', '=', 'active')]",
        ondelete="restrict",
    )

    @api.one
    @api.depends('journal_id')
    def _compute_bank_cheque_lot(self):
        Bank = self.env['res.partner.bank']
        if not self.journal_id:
            self.bank_id = False
            self.is_cheque_lot = False
            return
        bank = Bank.search([('journal_id', '=', self.journal_id.id)])
        if bank:
            self.bank_id = bank
            if bank.lot_ids:
                self.is_cheque_lot = True
        else:
            self.bank_id = False
            self.is_cheque_lot = False
