# -*- coding: utf-8 -*-

from openerp import models, fields
import time


class account_voucher(models.Model):

    _inherit = 'account.voucher'

    date_cheque = fields.Date(
        string='Cheque Date',
        default=lambda *a: time.strftime('%Y-%m-%d'))
    number_cheque = fields.Char(string='Cheque No.', size=64)
    bank_cheque = fields.Char(string='Bank', size=64)
    branch_cheque = fields.Char(string='Bank Branch', size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
