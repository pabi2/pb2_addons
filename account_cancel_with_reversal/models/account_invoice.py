# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancelled Journal Entry',
        copy=False,
    )

    @api.model
    def action_cancel_hook(self, moves=False):
        self.write({'state': 'cancel'})
        return
