# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    file_type = fields.Selection(
        selection_add=[('txt', 'Text')],
    )
