# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    pit_line = fields.One2many(
        'personal.income.tax',
        'voucher_id',
        string='Tax Line PIT',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
