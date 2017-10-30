# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    ship_expense = fields.Boolean(
        string='Shipping',
        copy=False,
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    ship_purchase_id = fields.Many2one(
        'purchase.order',
        string='For Purchase Order',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="This expense is shipping handling for things bought "
        "with this purchase order.",
    )

    @api.onchange('ship_expense')
    def _onchange_ship_expense(self):
        self.ship_purchase_id = False
