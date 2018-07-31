# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sequence = fields.Integer('Sequence', default=0)
