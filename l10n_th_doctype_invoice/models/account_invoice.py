# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        for invoice in self:
            # Find doctype
            refer_type = invoice.type
            if invoice.is_debitnote:
                refer_type += '_debitnote'
            doctype = self.env['res.doctype'].get_doctype(refer_type)
            # --
            invoice = invoice.with_context(doctype_id=doctype.id)
            super(AccountInvoice, invoice).action_move_create()
        return True
