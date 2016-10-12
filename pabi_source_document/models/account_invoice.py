# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    source_document_id = fields.Reference(
        [('purchase.order', 'Purchase'),
         ('sale.order', 'Sales'),
         ('hr.expense.expense', 'HR Expense'), ],
        string='Source Document Ref.',
        readonly=True,
    )
    source_document = fields.Char(
        string='Source Document Ref.',
        readonly=True,
    )

    @api.model
    def _prepare_refund(self, invoice, date=None, period_id=None,
                        description=None, journal_id=None):
        invoice_refund_vals = super(AccountInvoice, self).\
            _prepare_refund(invoice, date=date, period_id=period_id,
                            description=description, journal_id=journal_id)
        if invoice.source_document_id:
            invoice_refund_vals['source_document_id'] =\
                '%s,%s' % (invoice.source_document_id._model,
                           invoice.source_document_id.id)
            invoice_refund_vals['source_document'] = invoice.source_document
        return invoice_refund_vals
