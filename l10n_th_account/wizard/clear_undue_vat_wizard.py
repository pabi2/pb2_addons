# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ClearUndueVatWizard(models.TransientModel):
    _name = 'clear.undue.vat.wizard'

    date = fields.Date(
        string='Journal Entry Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
        help="Date for journal entry and tax sequence",
    )

    @api.multi
    def clear_undue_vat(self):
        active_id = self._context.get('active_id', False)
        voucher = self.env['account.voucher'].browse(active_id)
        ctx = self._context.copy()
        ctx.update({'recognize_vat': True,
                    'date_clear_undue': self.date, })
        voucher.with_context(ctx).proforma_voucher()
