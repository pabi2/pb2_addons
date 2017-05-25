# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

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
        res = super(HRSalaryExpense, self).action_cancel()
        period = self.env['account.period'].find()
        # First, set the invoices as cancelled and detach the move ids
        for salary in self:  # For each cancel invoice with internal_number
            move = salary.move_id
            if move:
                AccountMove = self.env['account.move']
                if move.line_id.filtered(lambda l: l.reconcile_id or
                                         l.reconcile_partial_id):
                    raise ValidationError(
                        _('This salary expensed has been partially '
                          'reconciles, cancellaion not allowed!'))
                move_dict = move.copy_data({
                    'name': move.name + '_VOID',
                    'ref': move.ref,
                    'period_id': period.id,
                    'date': fields.Date.context_today(self), })[0]
                move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
                rev_move = AccountMove.create(move_dict)
                AccountMove._reconcile_voided_entry([move.id, rev_move.id])
                rev_move.button_validate()
                salary.cancel_move_id = rev_move
        return res
