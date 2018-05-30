# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import time


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    purchase_billing_id = fields.Many2one(
        'purchase.billing',
        string='Billing Number',
        readonly=True,
        copy=False,
        index=True,
        ondelete='set null',
    )
    date_receipt_billing = fields.Date(
        string='Billing Receipt Date',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.constrains('date_receipt_billing')
    def _validate_date_receipt_billing(self):
        if self.date_receipt_billing < time.strftime('%Y-%m-%d'):
            raise ValidationError(
                _("You specified wrong billing receipt date "
                  "It must be more than or equal %s"
                    % (time.strftime('%d/%m/%Y'))))
