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
        copy=False,
    )
    source_document = fields.Char(
        string='Source Document Ref.',
        readonly=True,
        copy=False,
        size=500,
    )
    source_document_type = fields.Selection(
        [('purchase', 'Purchase Order'),
         ('sale', 'Sales Order'),
         ('expense', 'Expense'),
         ('advance', 'Advance')],
        string='Source Document Type',
        compute='_compute_source_document_type',
        store=True,
    )

    @api.multi
    @api.depends('source_document_id', 'reference')
    def _compute_source_document_type(self):
        for rec in self:
            if rec.source_document_id:
                if rec.source_document_id._name == 'purchase.order':
                    rec.source_document_type = 'purchase'
                if rec.source_document_id._name == 'sale.order':
                    rec.source_document_type = 'sale'
                if rec.source_document_id._name == 'hr.expense.expense':
                    if rec.source_document_id.is_employee_advance:
                        rec.source_document_type = 'advance'
                    else:
                        rec.source_document_type = 'expense'
            else:
                rec.source_document_type = False

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
