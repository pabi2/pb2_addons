# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountActivity(models.Model):
    _inherit = "account.activity"

    has_expense_rule = fields.Boolean(
        string='Has Expense Rule',
        default=False,
    )
    special_workflow = fields.Selection(
        [('fringe', 'Fringe'),
         ('recreation', 'Recreation')]
    )
