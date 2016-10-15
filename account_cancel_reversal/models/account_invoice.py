# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
    )

    @api.model
    def action_cancel_hook(self, moves=False):
        # Just change state, do not delete moves
        self.write({'state': 'cancel'})
        return

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        # First, set the invoices as cancelled and detach the move ids
        for inv in self:  # For each cancel invoice with internal_number
            move = inv.move_id
            if move:
                rev_move = move.copy({'name': move.name + '_VOID',
                                      'ref': move.ref})
                rev_move._switch_dr_cr()
                self.env['account.move'].\
                    _reconcile_voided_entry([move.id, rev_move.id])
                rev_move.button_validate()
                inv.cancel_move_id = rev_move
        # For invoice from DO, reset invoice_state to 2binvoiced
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        for inv in self:
            pickings = Picking.search([('name', '=', inv.origin)])
            if pickings:
                pickings.write({'invoice_state': '2binvoiced'})
                moves = Move.search([('picking_id', 'in', pickings._ids)])
                moves.write({'invoice_state': '2binvoiced'})

        return res
