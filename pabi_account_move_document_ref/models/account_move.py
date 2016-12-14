# -*- coding: utf-8 -*-
from openerp import models, fields, api

REFERENCE_SELECT = [('account.invoice', 'Invoice'),
                    ('account.voucher', 'Voucher'),
                    ('account.bank.receipt', 'Bank Receipt'),
                    ('stock.picking', 'Picking'),
                    ('interface.account.entry', 'Account Interface')]

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
                  ('interface_account', 'Account Interface')]

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

    document_ref = fields.Char(
        string='Origin Document',
        compute='_compute_document',
        store=True,
        readonly=True,
    )
    document_id = fields.Reference(
        REFERENCE_SELECT,
        string='Origin Document',
        compute='_compute_document',
        store=True,
        readonly=True,
    )
    document_type = fields.Selection(
        DOCTYPE_SELECT,
        string='Document Type',
        compute='_compute_document',
        store=True,
        help="Use selection as refer_type in res_doctype",
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
    # TODO: move is not in picking!!!
    # picking_ids = fields.One2many(
    #     'stock.picking',
    #     'move_id',
    #     string='Picking',
    #     readonly=True,
    # )
    account_interface_ids = fields.One2many(
        'interface.account.entry',
        'move_id',
        string='Account Interface',
        readonly=True,
    )

    @api.multi
    @api.depends('invoice_ids.move_id', 'invoice_cancel_ids.cancel_move_id',
                 'invoice_clear_prepaid_ids.clear_prepaid_move_id',
                 'voucher_ids.move_id', 'voucher_cancel_ids.cancel_move_id',
                 'voucher_recognize_vat_ids.recognize_vat_move_id',
                 'bank_receipt_ids.move_id',
                 'bank_receipt_cancel_ids.cancel_move_id',
                 # 'picking_ids.move_id',
                 'account_interface_ids.move_id')
    def _compute_document(self):
        for rec in self:
            model, _id = False, False
            # Invoice
            if rec.invoice_ids:
                model, _id = 'account.invoice', rec.invoice_ids[0].id
            if rec.invoice_cancel_ids:
                model, _id = 'account.invoice', rec.invoice_cancel_ids[0].id
            if rec.invoice_clear_prepaid_ids:
                model, _id = \
                    'account.invoice', rec.invoice_clear_prepaid_ids[0].id
            # Voucher
            if rec.voucher_ids:
                model, _id = 'account.voucher', rec.voucher_ids[0].id
            if rec.voucher_cancel_ids:
                model, _id = 'account.voucher', rec.voucher_cancel_ids[0].id
            if rec.voucher_recognize_vat_ids:
                model, _id = \
                    'account.voucher', rec.voucher_recognize_vat_ids[0].id
            # Bank Receipt
            if rec.bank_receipt_ids:
                model, _id = 'account.bank.receipt', rec.bank_receipt_ids[0].id
            if rec.bank_receipt_cancel_ids:
                model, _id = \
                    'account.bank.receipt', rec.bank_receipt_cancel_ids[0].id
            # Picking
            # if rec.picking_ids:
            #     model, _id = 'stock.picking', rec.picking_ids[0].id
            # Account Interface
            if rec.account_interface_ids:
                model, _id = \
                    'interface.account.entry', rec.account_interface_ids[0].id

            # Assign reference
            if model:
                rec.document_id = model and '%s,%s' % (model, _id) or False
                if model in ('stock.picking', 'account.bank.receipt'):
                    rec.document_ref = rec.document_id.name
                else:
                    rec.document_ref = rec.document_id.number
                rec.document_type = self._get_doctype(model, rec.document_id)

    @api.model
    def _get_doctype(self, model, document):
        if model == 'account.invoice':
            return INVOICE_DOCTYPE[document.journal_id.type]
        if model == 'account.voucher':
            return VOUCHER_DOCTYPE[document.type]
        if model == 'account.bank.receipt':
            return 'bank_receipt'
        if model == 'stock.picking':
            return PICKING_DOCTYPE[document.picking_type_id.code]
        if model == 'interface.account.entry':
            return 'interface_account'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    document_ref = fields.Char(
        string='Doc Ref',
        related='move_id.document_ref',
        store=True,
    )
    document_id = fields.Reference(
        REFERENCE_SELECT,
        string='Origin Document',
        related='move_id.document_id',
        store=True,
        readonly=True,
    )
    document_type = fields.Selection(
        DOCTYPE_SELECT,
        string='Document Type',
        related='move_id.document_type',
        store=True,
        help="Use selection as refer_type in res_doctype",
    )
