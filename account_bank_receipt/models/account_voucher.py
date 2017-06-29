# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    intransit = fields.Boolean(
        string='Bank Intransit',
        related='journal_id.intransit',
        readonly=True,
    )
    bank_receipt_id = fields.Many2one(
        'account.bank.receipt',
        string='Bank Receipt',
        compute='_compute_bank_receipt',
        store=True,
        readonly=True,
    )
    bank_receipt_name = fields.Char(
        string='Bank Receipt',
        related='bank_receipt_id.name',
        readonly=True,
    )

    @api.multi
    @api.depends('move_id.bank_receipt_id')
    def _compute_bank_receipt(self):
        for voucher in self:
            voucher.bank_receipt_id = voucher.move_id.bank_receipt_id

    @api.multi
    def action_open_bank_receipt(self):
        self.ensure_one()
        action = self.env.ref('account_bank_receipt.'
                              'action_bank_receipt_tree')
        result = action.read()[0]
        result.update({'domain': [('id', '=', self.bank_receipt_id.id)]})
        return result

    @api.multi
    def proforma_voucher(self):
        result = super(AccountVoucher, self).proforma_voucher()
        for voucher in self:
            if voucher.type == 'receipt' and voucher.intransit and \
                    self.env.user.company_id.auto_bank_receipt:
                receipt_date = fields.Date.context_today(self)
                voucher.move_id.create_bank_receipt(receipt_date)
        return result
