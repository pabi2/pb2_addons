# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    ar_late_move_line_id = fields.Many2one(
        'account.move.line',
        string='Referece to AR Late Penalty Move Line',
        readonly=True,
        help="Reference move line, so it will considered cleared for penalty"
    )
