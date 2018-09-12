# -*- coding: utf-8 -*-
import psycopg2
# import time
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def action_move_line_create(self):
        for voucher in self:
            # get doctype
            refer_type = voucher.type
            doctype = self.env['res.doctype'].get_doctype(refer_type)
            # --
            voucher = voucher.with_context(doctype_id=doctype.id)
            super(AccountVoucher, voucher).action_move_line_create()
        return True

    @api.multi
    def signal_workflow(self, trigger):
        """ Ensure that, when sequence is locked, it will repeat again """
        try:
            #  This part should not exists (but we need to avoid error)
            return super(AccountVoucher, self).signal_workflow(trigger)
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
