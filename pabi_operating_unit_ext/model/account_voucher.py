# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    operating_unit_id = fields.Many2one(
        required=True,
        domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class AccountVoucherLine(models.Model):
    _inherit = "account.voucher.line"

    operating_unit_id = fields.Many2one(required=False)
