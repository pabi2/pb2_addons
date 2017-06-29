# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def _prepare_inv_header(self, partner_id, expense):
        invoice_vals = super(HRExpenseExpense, self).\
            _prepare_inv_header(partner_id, expense)
        invoice_vals.update({
            'source_document_id': '%s,%s' % (self._model, expense.id),
            'source_document': expense.number,
        })
        return invoice_vals
