# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    auto_recognize_vat = fields.Boolean(
        string='Auto recognize undue VAT on Supplier Payment',
        related="company_id.auto_recognize_vat",
    )
    recognize_vat_journal_id = fields.Many2one(
        'account.journal',
        string='Recognize VAT Journal',
        related="company_id.recognize_vat_journal_id",
    )
