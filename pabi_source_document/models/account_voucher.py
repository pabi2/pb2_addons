# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    invoice_source_documents = fields.Char(
        string='Invoice Source Documents',
        compute='_compute_invoice_source_document',
        help="Source document of its related invoices",
    )

    @api.multi
    @api.depends('line_dr_ids', 'line_cr_ids')
    def _compute_invoice_source_document(self):
        for rec in self:
            invoices = \
                rec.line_ids.mapped('invoice_id').filtered('source_document')
            documents = invoices.mapped('source_document')
            rec.invoice_source_documents = ', '.join(documents)
