# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    bank_id = fields.Many2one(
        'res.partner.bank',
        related='journal_id.bank_id',
        string='Bank Account',
    )
    is_cheque_lot = fields.Boolean(
        string='Is Cheque Lot Available',
        compute='_compute_is_cheque_lot',
    )
    cheque_lot_id = fields.Many2one(
        'cheque.lot',
        string='Cheque Lot',
        domain="[('bank_id', '=', bank_id), "
        "('journal_id', '=', journal_id), ('state', '=', 'active')]",
        ondelete="restrict",
    )

    @api.one
    @api.depends('bank_id', 'journal_id')
    def _compute_is_cheque_lot(self):
        Lot = self.env['cheque.lot']
        lots = Lot.search([('bank_id', '=', self.bank_id.id),
                           ('journal_id', '=', self.journal_id.id)])
        self.is_cheque_lot = lots and True or False
