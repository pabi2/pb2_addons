# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    # For reporting purpose only
    line_ids_name = fields.Text(
        compute='_compute_line_ids',
    )
    line_ids_amount = fields.Text(
        compute='_compute_line_ids',
    )
    # --

    @api.multi
    def _compute_line_ids(self):
        for rec in self:
            lines = rec.bank_intransit_ids.sorted(key=lambda l: l.ref)
            payments = lines.mapped('ref')
            amounts = lines.mapped(lambda l: l.debit - l.credit)
            amounts = ['{:,.2f}'.format(amount) for amount in amounts]
            rec.line_ids_name = '\n'.join(payments)
            rec.line_ids_amount = '\n'.join(amounts)
