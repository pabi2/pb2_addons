# -*- coding: utf-8 -*-
from openerp import models, fields, api

REFERENCE_SELECT = [('account.invoice', 'Invoice'),
                    ('account.voucher', 'Voucher'),
                    ('account.bank.receipt', 'Bank Receipt'),
                    ('stock.picking', 'Picking'),
                    ('interface.account.entry', 'Account Interface'),
                    ('hr.expense.expense', 'Employee Expense'),
                    ('hr.salary.expense', 'Salary Expense'),
                    # For analytic line only (budget commitment)
                    ('purchase.request', 'Purchase Request'),
                    ('purchase.order', 'Purchase Order'),
                    ('sale.order', 'Sales Order'),
                    ]

DOCTYPE_SELECT = [('incoming_shipment', 'Incoming Shipment'),
                  ('delivery_order', 'Delivery Order'),
                  ('internal_transfer', 'Internal Transfer',),
                  ('bank_receipt', 'Bank Receipt'),
                  ('out_invoice', 'Customer Invoice'),
                  ('out_refund', 'Customer Refund'),
                  ('out_invoice_debitnote', 'Customer Debitnote'),
                  ('in_invoice', 'Supplier Invoice'),
                  ('in_refund', 'Supplier Refund'),
                  ('in_invoice_debitnote', 'Supplier Debitnote'),
                  ('receipt', 'Customer Payment'),
                  ('payment', 'Supplier Payment'),
                  ('employee_expense', 'Employee Expense'),
                  ('salary_expense', 'Salary Expense'),
                  ('interface_account', 'Account Interface'),
                  # For analytic line only (budget commitment)
                  ('purchase_request', 'Purchase Request'),
                  ('purchase_order', 'Purchase Order'),
                  ('sale_order', 'Sales Order'),
                  # Non document related, adjustment
                  ('adjustment', 'Adjustment'),
                  # Special Type for Monitoring Report
                  ('account_budget', 'Budget Control')]

INVOICE_DOCTYPE = {'sale': 'out_invoice',
                   'sale_refund': 'out_refund',
                   'sale_debitnote': 'out_invoice_debitnote',
                   'purchase': 'in_invoice',
                   'purchase_refund': 'in_refund',
                   'purchase_debitnote': 'in_invoice_debitnote', }

VOUCHER_DOCTYPE = {'receipt': 'receipt',
                   'payment': 'payment', }

PICKING_DOCTYPE = {'incoming': 'incoming_shipment',
                   'outgoing': 'delivery_order',
                   'internal': 'internal_transfer', }


class AccountMove(models.Model):
    _inherit = 'account.move'

    document = fields.Char(
        string='Document',
        compute='_compute_document',
        store=True,
        readonly=True,
    )
    document_id = fields.Reference(
        REFERENCE_SELECT,
        string='Document',
        compute='_compute_document',
        store=True,
        readonly=True,
    )
    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        compute='_compute_document',
        store=True,
        index=True,
        help="Use selection as refer_type in res_doctype",
    )
    date_value = fields.Date(
        string='Value Date',
        compute='_compute_document',
        store=True,
        help="If origin document have value date. Otherwise, use move date",
    )
    invoice_ids = fields.One2many(
        'account.invoice',
        'move_id',
        string='Invoice',
        readonly=True,
    )
    invoice_cancel_ids = fields.One2many(
        'account.invoice',
        'cancel_move_id',
        string='Invoice Cancel',
        readonly=True,
    )
    invoice_clear_prepaid_ids = fields.One2many(
        'account.invoice',
        'clear_prepaid_move_id',
        string='Invoice Clear Prepaid',
        readonly=True,
    )
    voucher_ids = fields.One2many(
        'account.voucher',
        'move_id',
        string='Payment',
        readonly=True,
    )
    voucher_cancel_ids = fields.One2many(
        'account.voucher',
        'cancel_move_id',
        string='Payment Cancel',
        readonly=True,
    )
    voucher_recognize_vat_ids = fields.One2many(
        'account.voucher',
        'recognize_vat_move_id',
        string='Payment Recognize VAT',
        readonly=True,
    )
    bank_receipt_ids = fields.One2many(
        'account.bank.receipt',
        'move_id',
        string='Bank Receipt',
        readonly=True,
    )
    bank_receipt_cancel_ids = fields.One2many(
        'account.bank.receipt',
        'cancel_move_id',
        string='Bank Receipt Cancel',
        readonly=True,
    )
    salary_expense_ids = fields.One2many(
        'hr.salary.expense',
        'move_id',
        string='Salary Expense',
        readonly=True,
    )
    salary_expense_cancel_ids = fields.One2many(
        'hr.salary.expense',
        'cancel_move_id',
        string='Salary Expense Cancel',
        readonly=True,
    )
    expense_rev_ic_ids = fields.One2many(
        'hr.expense.expense',
        'rev_ic_move_id',
        string='IC Revenue',
        readonly=True,
    )
    expense_exp_ic_ids = fields.One2many(
        'hr.expense.expense',
        'exp_ic_move_id',
        string='IC Expense',
        readonly=True,
    )
    account_interface_ids = fields.One2many(
        'interface.account.entry',
        'move_id',
        string='Account Interface',
        readonly=True,
    )

    @api.multi
    @api.depends('invoice_ids.internal_number',
                 'invoice_cancel_ids.internal_number',
                 'invoice_clear_prepaid_ids.internal_number',
                 'voucher_ids.number',
                 'voucher_cancel_ids.number',
                 'voucher_recognize_vat_ids.number',
                 'bank_receipt_ids.name',
                 'bank_receipt_cancel_ids.name',
                 'salary_expense_ids.name',
                 'salary_expense_cancel_ids.name',
                 'expense_rev_ic_ids.number',
                 'expense_exp_ic_ids.number',
                 'account_interface_ids.number',
                 'ref',  # check for stock.picking case, as it has no move_id
                 )
    def _compute_document(self):
        for rec in self:
            document = False
            # Invoice
            if rec.invoice_ids:
                document = rec.invoice_ids[0]
            elif rec.invoice_cancel_ids:
                document = rec.invoice_cancel_ids[0]
            elif rec.invoice_clear_prepaid_ids:
                document = rec.invoice_clear_prepaid_ids[0]
            # Voucher
            elif rec.voucher_ids:
                document = rec.voucher_ids[0]
            elif rec.voucher_cancel_ids:
                document = rec.voucher_cancel_ids[0]
            elif rec.voucher_recognize_vat_ids:
                document = rec.voucher_recognize_vat_ids[0]
            # Bank Receipt
            elif rec.bank_receipt_ids:
                document = rec.bank_receipt_ids[0]
            elif rec.bank_receipt_cancel_ids:
                document = rec.bank_receipt_cancel_ids[0]
            # Salary Expense
            elif rec.salary_expense_ids:
                document = rec.salary_expense_ids[0]
            elif rec.salary_expense_cancel_ids:
                document = rec.salary_expense_cancel_ids[0]
            # Expense IC
            elif rec.expense_rev_ic_ids:
                document = rec.expense_rev_ic_ids[0]
            elif rec.expense_exp_ic_ids:
                document = rec.expense_exp_ic_ids[0]
            # Account Interface
            elif rec.account_interface_ids:
                document = rec.account_interface_ids[0]
            elif rec.ref:  # Last chance for picking, as it not have move_id
                Picking = self.env['stock.picking']
                picking = Picking.search([('name', '=', rec.ref)])
                document = picking and picking[0] or False

            # Assign reference
            if document:
                rec.document_id = '%s,%s' % (document._name, document.id)
                if document._name in ('stock.picking', 'account.bank.receipt'):
                    rec.document = document.name
                elif document._name == 'account.invoice':
                    rec.document = document.internal_number
                else:
                    rec.document = document.number
                rec.doctype = self._get_doctype(document._name, document)
                if 'date_value' in document._fields:
                    rec.date_value = document.date_value
            else:
                rec.doctype = 'adjustment'  # <-- Not related to any doc
            if not rec.date_value:
                rec.date_value = rec.date  # No Value Date, same as date

    @api.model
    def _get_doctype(self, model, document):
        if model == 'account.invoice':
            return INVOICE_DOCTYPE[document.journal_id.type]
        if model == 'account.voucher':
            return VOUCHER_DOCTYPE[document.type]
        if model == 'account.bank.receipt':
            return 'bank_receipt'
        if model == 'hr.expense.expense':
            return 'employee_expense'
        if model == 'hr.salary.expense':
            return 'salary_expense'
        if model == 'stock.picking':
            return PICKING_DOCTYPE[document.picking_type_id.code]
        if model == 'interface.account.entry':
            return 'interface_account'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    document = fields.Char(
        string='Document',
        related='move_id.document',
        store=True,
        readonly=True,
    )
    document_id = fields.Reference(
        REFERENCE_SELECT,
        string='Document',
        related='move_id.document_id',
        store=True,
        readonly=True,
    )
    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        related='move_id.doctype',
        store=True,
        readonly=True,
        help="Use selection as refer_type in res_doctype",
    )
    date_value = fields.Date(
        string='Value Date',
        related='move_id.date_value',
        store=True,
        readonly=True,
        help="If origin document have value date. Otherwise, use move date",
    )
