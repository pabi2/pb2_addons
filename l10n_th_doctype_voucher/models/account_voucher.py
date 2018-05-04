# -*- coding: utf-8 -*-
from openerp import models, api


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
