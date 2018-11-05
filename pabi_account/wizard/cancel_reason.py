# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoiceCancel(models.TransientModel):
    _inherit = 'account.invoice.cancel'

    cancel_date_document = fields.Date(
        string='Cancel Document Date',
        required=True,
    )
    cancel_date = fields.Date(
        string='Cancel Posting Date',
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(AccountInvoiceCancel, self).default_get(field_list)
        Invoice = self.env['account.invoice']
        invoice = Invoice.browse(self._context.get('active_id'))
        res['cancel_date_document'] = invoice.move_id and \
            invoice.move_id.date_document or invoice.date_document
        res['cancel_date'] = invoice.move_id and \
            invoice.move_id.date or invoice.date_invoice
        return res

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        invoice_ids = self._context.get('active_ids')
        assert len(invoice_ids) == 1, "Only 1 invoice expected"
        invoice = self.env['account.invoice'].browse(invoice_ids)
        invoice.write({'cancel_date_document': self.cancel_date_document,
                       'cancel_date': self.cancel_date})
        return super(AccountInvoiceCancel, self).confirm_cancel()


class AccountVoucherCancel(models.TransientModel):
    _inherit = 'account.voucher.cancel'

    cancel_date_document = fields.Date(
        string='Cancel Document Date',
        required=True,
    )
    cancel_date = fields.Date(
        string='Cancel Posting Date',
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(AccountVoucherCancel, self).default_get(field_list)
        Voucher = self.env['account.voucher']
        voucher = Voucher.browse(self._context.get('active_id'))
        res['cancel_date_document'] = voucher.move_id and \
            voucher.move_id.date_document or voucher.date_document
        res['cancel_date'] = voucher.move_id and \
            voucher.move_id.date or voucher.date
        return res

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        voucher_ids = self._context.get('active_ids')
        assert len(voucher_ids) == 1, "Only 1 payment expected"
        voucher = self.env['account.voucher'].browse(voucher_ids)
        voucher.write({'cancel_date_document': self.cancel_date_document,
                       'cancel_date': self.cancel_date})
        return super(AccountVoucherCancel, self).confirm_cancel()


class AccountBankReceiptCancel(models.TransientModel):
    _inherit = 'account.bank.receipt.cancel'

    cancel_date_document = fields.Date(
        string='Cancel Document Date',
        required=True,
    )
    cancel_date = fields.Date(
        string='Cancel Posting Date',
        required=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(AccountBankReceiptCancel, self).default_get(field_list)
        BankReceipt = self.env['account.bank.receipt']
        receipt = BankReceipt.browse(self._context.get('active_id'))
        res['cancel_date_document'] = receipt.move_id and \
            receipt.move_id.date_document or receipt.date_document
        res['cancel_date'] = receipt.move_id and \
            receipt.move_id.date or receipt.receipt_date
        return res

    @api.multi
    def confirm_cancel(self):
        self.ensure_one()
        receipt_ids = self._context.get('active_ids')
        assert len(receipt_ids) == 1, "Only 1 bank receipt expected"
        receipt = self.env['account.bank.receipt'].browse(receipt_ids)
        receipt.write({'cancel_date_document': self.cancel_date_document,
                       'cancel_date': self.cancel_date})
        return super(AccountBankReceiptCancel, self).confirm_cancel()
