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
        loan_ids = self._context.get('active_ids', [])
        for loan in LoanObj.browse(loan_ids):
            loan.update_invoice_lines({'section_id': self.section_id.id})
            self._cr.execute("""
                update loan_customer_agreement
                set section_id=%d where
                id=%d
            """ % (self.section_id.id, loan.id))
