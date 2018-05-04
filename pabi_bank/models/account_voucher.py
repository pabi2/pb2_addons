# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    supplier_bank_branch = fields.Char(
        string='Supplier Bank Branch',
        related='supplier_bank_id.bank_branch.name',
        readonly=True,
    )
