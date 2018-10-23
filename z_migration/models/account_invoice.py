# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    type = fields.Selection(
        readonly=False,
    )

    @api.multi
    def mock_trigger_workflow(self, signal):
        """ Because openerplib can't call workflow directly, we mock it """
        self.signal_workflow(signal)
        return True

    @api.multi
    def mock_button_reset_taxes(self):
        self.button_reset_taxes()
        return True
