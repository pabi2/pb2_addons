# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ResDoctype(models.Model):
    _name = 'res.doctype'
    _description = 'Doctype'

    name = fields.Char(
        string='Name',
        readonly=True,
    )
    refer_type = fields.Selection([
        # Sale / Purchase
        ('sale_quotation', 'Sales Quotation'),
        ('purchase_quotation', 'Purchase Quotation'),
        ('sale_order', 'Sales Order'),
        ('purchase_order', 'Purchase Order'),
        # Voucher Types
        ('sale', 'Sales Receipt'),
        ('purchase', 'Purchase Receipt'),
        ('payment', 'Supplier Payment'),
        ('receipt', 'Customer Payment'),
        # Invoice Types
        ('out_invoice', 'Customer Invoice'),
        ('out_invoice_debitnote', 'Customer Debitnote'),
        ('in_invoice', 'Supplier Invoice'),
        ('in_invoice_debitnote', 'Supplier Debitnote'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
        # Expense
        ('employee_expense', 'Employee Expense'),
        ('employee_advance', 'Employee Advance'),
        # Stock
        ('incoming_shipment', 'Incoming Shipment'),
        ('delivery_order', 'Delivery Order'),
        ('internal_transfer', 'Internal Transfer'),
        ],
        string='Reference Document',
        readonly=True,
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
        domain=[('special_type', '=', 'doctype')],
    )
    prefix = fields.Char(
        related='sequence_id.prefix',
        string='Prefix',
    )
    implementation = fields.Selection(
        [('standard', 'Standard'),
         ('no_gap', 'No gap'), ],
        related='sequence_id.implementation',
        string='Implementation',
    )

    @api.model
    def get_doctype(self, refer_type):
        doctype = self.search([('refer_type', '=', refer_type)], limit=1)
        return doctype
