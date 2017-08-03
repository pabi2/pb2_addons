# -*- coding: utf-8 -*-
import ast
from openerp import models, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_create_payment(self):
        action_id = False
        if 'in' in self[0].type:
            action_id = self.env.ref('account_voucher.action_vendor_payment')
        if 'out' in self[0].type:
            action_id = self.env.ref('account_voucher.action_vendor_receipt')
        if not action_id:
            raise ValidationError(_('No Action'))
        action = action_id.read([])[0]
        ctx = ast.literal_eval(action['context'])
        ctx.update({
            'filter_invoices': self.ids  # account_move_line.search()
        })
        action['context'] = ctx
        action['views'].reverse()
        return action
