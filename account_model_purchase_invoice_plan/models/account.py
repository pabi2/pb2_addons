# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountModel(models.Model):
    _inherit = 'account.model'

    use_purchase_invoice_plan = fields.Boolean(
        string='Use Purchase Invoice Plan',
        default=False,
    )

    @api.onchange('use_purchase_invoice_plan')
    def _onchange_use_purchase_invoice_plan(self):
        if self.use_purchase_invoice_plan:
            self.lines_id = []
            self.lines_id = False
