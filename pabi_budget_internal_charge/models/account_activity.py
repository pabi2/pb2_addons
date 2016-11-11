# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountActivity(models.Model):
    _inherit = "account.activity"

    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        required=True,
        default='expense',
    )
