# -*- coding: utf-8 -*-
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def mock_trigger_workflow(self, signal):
        """ Because openerplib can't call workflow directly, we mock it """
        self.signal_workflow(signal)
        return True
