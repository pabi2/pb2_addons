# -*- coding: utf-8 -*-
from openerp import models, fields, api


class VoucherInvoiceDescription(models.TransientModel):
    _name = "voucher.invoice.description"
    _description = "Invoice Description"

    invoice_description = fields.Text(
        string="Invoice Description",
        size=1000,
        default=lambda self: self._default_invoice_description(),
    )

    @api.model
    def _default_invoice_description(self):
        active_id = self._context.get('active_id')
        voucher_line = self.env['account.voucher.line'].browse(active_id)
        description = voucher_line.invoice_id.invoice_description
        return description

    @api.multi
    def action_save(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        voucher_line = self.env['account.voucher.line'].browse(active_id)
        if voucher_line.invoice_id:
            voucher_line.invoice_id.invoice_description = \
                self.invoice_description
