# -*- coding: utf-8 -*-

from openerp import models, fields,  api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cancel_move_id = fields.Many2one('account.move', 'Cancelled Journal Entry')

    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
#             if inv.move_id:
#                 moves += inv.move_id
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
