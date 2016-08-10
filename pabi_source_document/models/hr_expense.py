# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.multi
    def _create_supplier_invoice_from_expense(self, merge_line=False):
        invoice = super(HRExpenseExpense, self).\
            _create_supplier_invoice_from_expense()
        if invoice:
            for expense in self:
                invoice.write({'source_document_id': '%s,%s'
                               % (self._model, expense.id)})
        return invoice
