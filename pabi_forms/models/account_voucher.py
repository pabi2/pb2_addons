# -*- encoding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

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
            lines = rec.line_ids.sorted(key=lambda l: l.move_line_id.name)
            invoices = lines.mapped('invoice_id')
            amounts = lines.mapped('amount')
            amounts = ['{:,.2f}'.format(amount) for amount in amounts]
            rec.line_ids_name = '\n'.join(invoices.mapped('number'))
            rec.line_ids_amount = '\n'.join(amounts)
