# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ref_invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Ref Invoice Line',
        readonly=True,
        help="Reference back to origin invoice document",
    )
