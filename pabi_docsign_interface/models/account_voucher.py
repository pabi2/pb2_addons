# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    state_sign = fields.Selection([
        ('waiting', 'Waiting'),
        ('signed', 'Signed'), ],
        string="State Sign",
        default="waiting",
        readonly=True,
    )
    number_preprint_current = fields.Char(
        string='Preprint Signed',
        readonly=True,
    )
