# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    rpt_activity_id = fields.Many2one(
        'account.activity',
        string='Rpt Activity',
        required=True,
    )

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        self.rpt_activity_id = self.activity_id
