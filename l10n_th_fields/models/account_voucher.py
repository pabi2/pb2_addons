# -*- coding: utf-8 -*-

from openerp import models, fields
import time


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    # Customer Payment
    date_cheque = fields.Date(
        string='Cheque Date',
        default=lambda *a: time.strftime('%Y-%m-%d'),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    number_cheque = fields.Char(
        string='Cheque No.',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    bank_cheque = fields.Char(
        string='Bank',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    branch_cheque = fields.Char(
        string='Bank Branch',
        size=64,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # Supplier Payment
    date_value = fields.Date(
        string='Value Date',  # bank transfer date
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
