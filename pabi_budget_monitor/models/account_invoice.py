# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_cancel(self):
        self = self.with_context(force_no_budget_check=True)
        return super(AccountInvoice, self).action_cancel()
