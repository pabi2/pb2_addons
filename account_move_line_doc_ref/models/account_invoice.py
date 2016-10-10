# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if invoice.move_id:
                invoice.move_id.line_id.write(
                    {'doc_ref': invoice.number,
                     'doc_id': '%s,%s' % ('account.invoice', invoice.id)},
                    check=False, update_check=False)
        return result
