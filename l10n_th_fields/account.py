# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
    )
