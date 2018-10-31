# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountBankReceipt(models.Model):
    _inherit = "account.bank.receipt"

    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        domain="[('partner_id', '=', company_partner_id)]",
        required=False,
    )
    bank_account_id = fields.Many2one(
        'account.account',
        related=False,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    receipt_date = fields.Date(
        string='Posting Date',  # Change label
    )
    date_document = fields.Date(
        string='Document Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        default=lambda self: fields.Date.context_today(self),
    )
    date_accept = fields.Date(
        string='Accepted Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def write(self, vals):
        # Set date
        if vals.get('receipt_date') and not vals.get('date_document'):
            for rec in self:
                if not rec.date_document:
                    vals['date_document'] = vals['receipt_date']
                    break
        return super(AccountBankReceipt, self).write(vals)

    @api.onchange('bank_account_id')
    def onchange_bank_account_id(self):
        self.partner_bank_id = False
        if self.bank_account_id:
            Journal = self.env['account.journal']
            BankAcct = self.env['res.partner.bank']
            journals = Journal.search([('default_debit_account_id', '=',
                                        self.bank_account_id.id)])
            banks = BankAcct.search([('journal_id', 'in', journals.ids),
                                     ('state', '=', 'SA')])
            self.partner_bank_id = banks and banks[0] or False
