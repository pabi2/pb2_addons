# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
