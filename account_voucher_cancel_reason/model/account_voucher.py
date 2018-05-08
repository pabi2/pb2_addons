# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    cancel_reason_txt = fields.Char(
        string="Description",
        readonly=True)
