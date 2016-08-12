from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    invoice_type = fields.Selection(
        [('normal', 'Normal Invoice')],
        string="Invoice Type",
        readonly=True,
        copy=False,
        default='normal',
    )
