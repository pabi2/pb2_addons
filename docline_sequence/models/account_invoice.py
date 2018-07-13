# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID
from .common import DoclineCommon, DoclineCommonSeq


class AccountInvoice(DoclineCommon, models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.constrains('invoice_line')
    def _check_docline_seq(self):
        for invoice in self:
            self._compute_docline_seq('account_invoice_line',
                                      'invoice_id', invoice.id)
        return True


class AccountInvoiceLine(DoclineCommonSeq, models.Model):
    _inherit = 'account.invoice.line'

    def init(self, cr):
        """ On module update, recompute all documents """
        self.pool.get('account.invoice').\
            _recompute_all_docline_seq(cr, SUPERUSER_ID,
                                       'account_invoice',
                                       'account_invoice_line',
                                       'invoice_id')
