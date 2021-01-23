# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    state_sign = fields.Selection([
        ('waiting', 'Waiting'),
        ('signed', 'Signed'),
        ('cancel', 'Cancelled'),
        ],
        string="State Sign",
        default="waiting",
        readonly=True,
    )
