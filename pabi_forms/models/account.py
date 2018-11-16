# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_account_ids = fields.One2many(
        'res.partner.bank',
        'journal_id',
        string='Bank Accounts',
        readonly=True,
    )
