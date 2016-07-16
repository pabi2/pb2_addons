# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    customer_amount = fields.Float(
        string='Customer Payment',
        help="Specify the customer payment value.\
            Value specified here will be used in \
            contra entry for payment journal.",
        digits_compute=dp.get_precision('Account'),
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    supplier_amount = fields.Float(
        string='Supplier Payment',
        help="Specify the supplier payment value.\
            Value specified here will be used in\
            contra entry for payment journal.",
        digits_compute=dp.get_precision('Account'),
        required=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def _set_local_context(self):
        return self._context
