# -*- coding: utf-8 -*-
from openerp import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    # Change order debit first then credit. Can't do much as it affect perf
    _order = 'move_id, debit desc, credit desc , account_id'
