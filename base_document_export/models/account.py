# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    file_type = fields.Selection(
        selection=[],
        string='File Type',
        required=False,
    )
