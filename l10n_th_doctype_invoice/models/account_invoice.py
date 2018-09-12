# -*- coding: utf-8 -*-
import psycopg2
import time
from openerp import models, api, _
from openerp.exceptions import ValidationError


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

    @api.multi
    def signal_workflow(self, trigger):
        try:
            # with self._cr.savepoint():
            return super(AccountInvoice, self).signal_workflow(trigger)
        except psycopg2.OperationalError:
            # Let's retry 3 times, each to wait 0.5 seconds
            retry = self._context.get('retry', 1)
            if retry <= 5:
                time.sleep(0.5)
                retry += 1
                self._cr.rollback()
                return self.with_context(retry=retry).signal_workflow(trigger)
            raise ValidationError(
                _('Waiting for next number, please try again later!'))
        except Exception:
            raise
