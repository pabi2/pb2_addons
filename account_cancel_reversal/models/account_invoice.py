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
                AccountMove = self.env['account.move']
                move_data = inv._prepare_reverse_move_data()
                move_dict = move.copy_data(move_data)[0]
                move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
                rev_move = AccountMove.create(move_dict)
                AccountMove.\
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

    @api.multi
    def _prepare_reverse_move_data(self):
        self.ensure_one()
        move = self.move_id
        date = fields.Date.context_today(self)
        periods = self.env['account.period'].find(date)
        period = periods and periods[0] or False
        return {
            'name': move.name + '_VOID',
            'ref': move.ref,
            'period_id': period.id,
            'date': date,
        }
