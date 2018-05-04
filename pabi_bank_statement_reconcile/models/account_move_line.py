# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    match_import_id = fields.Many2one(
        'pabi.bank.statement.import',
        string='Matched Import ID',
        ondelete='set null',
    )
