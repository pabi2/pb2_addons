# -*- coding: utf-8 -*-
from openerp import api, models, fields


class UpdateSectionInvoice(models.TransientModel):
    _name = 'update.section.invoice'

    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )

    @api.multi
    def action_update_section(self):
        self.ensure_one()
        LoanObj = self.env['loan.customer.agreement']
        InvoiceObj = self.env['account.invoice']
        InvoiceLineObj = self.env['account.invoice.line']
        loan_ids = self._context.get('active_ids', [])
        for loan in LoanObj.browse(loan_ids):
            invoice_ids = InvoiceObj.search([('loan_agreement_id', '=', loan.id),
                                             ('state', '=', 'draft')]).ids
            invoice_lines =\
                InvoiceLineObj.search([('invoice_id', 'in', invoice_ids)])
            for line in invoice_lines:
                line.write({'section_id': self.section_id.id})
