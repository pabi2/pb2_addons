# -*- coding: utf-8 -*-
from openerp import models, fields


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    date_dunning_1 = fields.Date(
        string='1st Notice',
        readonly=True,
    )
    date_dunning_2 = fields.Date(
        string='2nd Notice',
        readonly=True,
    )
    date_dunning_3 = fields.Date(
        string='3rd Notice',
        readonly=True,
    )
