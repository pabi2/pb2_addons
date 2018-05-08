# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .account_move import REFERENCE_SELECT, DOCTYPE_SELECT


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    document = fields.Char(
        string='Document',
        compute='_compute_document',
        store=True,
        readonly=True,
    )
    document_line = fields.Char(
        string='Document Line',
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
        help="Use selection as refer_type in res_doctype",
    )

    @api.multi
    @api.depends('move_id', 'expense_id', 'sale_id',
                 'purchase_request_id', 'purchase_id')
    def _compute_document(self):
        for rec in self:
            if rec.move_id:
                rec.document = rec.move_id.document
                rec.document_line = rec.name
                rec.document_id = rec.move_id.document_id
                rec.doctype = rec.move_id.doctype
            elif rec.expense_id:
                rec.document = rec.expense_id.number
                rec.document_line = rec.expense_line_id.name
                rec.document_id = \
                    '%s,%s' % ('hr.expense.expense', rec.expense_id.id)
                rec.doctype = 'employee_expense'
            elif rec.purchase_request_id:
                rec.document = rec.purchase_request_id.name
                rec.document_line = rec.purchase_request_line_id.name
                rec.document_id = \
                    '%s,%s' % ('purchase.request', rec.purchase_request_id.id)
                rec.doctype = 'purchase_request'
            elif rec.purchase_id:
                rec.document = rec.purchase_id.name
                rec.document_line = rec.purchase_line_id.name
                rec.document_id = \
                    '%s,%s' % ('purchase.order', rec.purchase_id.id)
                rec.doctype = 'purchase_order'
            elif rec.sale_id:
                rec.document = rec.sale_id.name
                rec.document_line = rec.sale_line_id.name
                rec.document_id = \
                    '%s,%s' % ('sale.order', rec.sale_id.id)
                rec.doctype = 'sale_order'
