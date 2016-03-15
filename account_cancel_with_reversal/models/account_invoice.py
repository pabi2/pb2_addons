# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cancel_move_id = fields.Many2one(
        'account.move',
        'Cancelled Journal Entry',
        copy=False
        )

    @api.multi
    def action_cancel(self):
        for inv in self:
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise Warning(_('Error!'),
                                      _('You cannot cancel an invoice\
                                        which is partially paid. You need \
                                        to unreconcile related \
                                        payment entries first.'))
        self.write({'state': 'cancel'})
        return True
