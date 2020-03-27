# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        if self._context.get('is_clear_prepaid', False):
            # For clear prepayment we don't want to pass invoice number
            self = self.with_context(invoice=False)
        move = super(AccountMove, self).create(vals)
        return move


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    cash_on_delivery = fields.Boolean(
        string='Cash On Delivery',
        default=False,
        help="If checked, this term is payment in advance",
    )


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    clear_prepaid_profit_loss = fields.Many2one(
        'account.account',
        string='Prepaid Profit and Loss',
        help="create new profit/loss line for clear prepaid only",
    )
    clear_prepaid_ag = fields.Many2one(
        'account.activity.group',
        string='Prepaid Activity Group',
        help="activity group of new profit/loss for clear prepaid only"
    )
    clear_prepaid_activity = fields.Many2one(
        'account.activity',
        string='Prepaid Activity',
        help="activity of new profit/loss for clear prepaid only"
    )
