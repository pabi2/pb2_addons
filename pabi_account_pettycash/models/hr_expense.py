# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        selection_add=[('pettycash', 'Petty Cash')],
    )
    pettycash_id = fields.Many2one(
        'account.pettycash',
        string='Petty Cash',
        ondelete='restrict',
    )
