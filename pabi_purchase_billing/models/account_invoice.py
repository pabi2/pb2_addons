# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import time


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _order = "date_document asc,invoice_plan_ids asc"
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
        copy=False,
        states={'draft': [('readonly', False)]},
    )

    @api.constrains('date_receipt_billing')
    def _validate_date_receipt_billing(self):
        date_receipt_billing = self.date_receipt_billing
        if date_receipt_billing:
            if date_receipt_billing < time.strftime('%Y-%m-%d'):
                raise ValidationError(
                    _("You specified wrong billing receipt date "
                      "It must be more than or equal %s"
                      % (time.strftime('%d/%m/%Y'))))
        return True

    @api.multi
    def recover_cancelled_invoice(self):
        """ When recreated link billing from previous invoice """
        self.ensure_one()
        res = super(AccountInvoice, self).recover_cancelled_invoice()
        # Stamp Billing to this invoice
        self.recreated_invoice_id.write({
            'purchase_billing_id': self.purchase_billing_id.id,
            # 'date_receipt_billing': self.date_receipt_billing,
        })
        # Stamp Invoice to this billing
        self.purchase_billing_id.write({
            'supplier_invoice_ids': [(4, self.recreated_invoice_id.id)]
        })
        return res
