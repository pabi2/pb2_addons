# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountMoveReverse(models.TransientModel):
    _inherit = 'account.move.reverse'

    move_prefix = fields.Char(
        default=lambda self: self._default_move_prefix(),
    )

    @api.model
    def view_init(self, fields_list):
        """ Allow only Adjustment Journal to be reversed """
        res_model = self._context.get('active_model', False)
        res_id = self._context.get('active_id', False)
        exp_reverse_move = self._context.get('reverse_move', False)
        move = self.env[res_model].browse(res_id)
        if exp_reverse_move:
            move = move.exp_ic_move_id
        # allow Expense: Internal Charge,Revenue: Internal Charge
        if not move.journal_id.id in [7, 6]:
            if move.doctype not in ('adjustment', 'interface_account'):
                raise ValidationError(
                    _('No direct reverse allowed for non adjustment doctype!\n'
                      'You should make reverse on source document.'))

    @api.model
    def _default_move_prefix(self):
        move_ids = self._context.get('active_ids', False)
        exp_reverse_move = self._context.get('reverse_move', False)
        if exp_reverse_move:
            return False
        if move_ids and len(move_ids) == 1:
            move = self.env['account.move'].browse(move_ids[0])
            return '%s - ' % move.name

    def action_reverse(self, cr, uid, ids, context=None):
        res_model = context.get('active_model', False)
        res_id = context.get('active_id', False)
        exp_reverse_move = context.get('reverse_move', False)
        expense = \
            self.pool.get(res_model).browse(cr, uid, res_id, context=context)

        if exp_reverse_move:
            context = context.copy()
            if expense.exp_ic_move_id:
                context.update({'active_ids': expense.exp_ic_move_id.id})
                exp_move = expense.exp_ic_move_id
                wizard = self.browse(cr, uid, ids, context)
                wizard.move_prefix = '%s - ' % exp_move.name
                res = super(AccountMoveReverse, self).action_reverse(
                    cr, uid, ids, context=context)
                reversal = expense.exp_ic_move_id.reversal_id
                if reversal:
                    reversal.button_validate()
            if expense.rev_ic_move_id:
                context.update({'active_ids': expense.rev_ic_move_id.id})
                exp_move = expense.rev_ic_move_id
                wizard = self.browse(cr, uid, ids, context)
                wizard.move_prefix = '%s - ' % exp_move.name
                res = super(AccountMoveReverse, self).action_reverse(
                    cr, uid, ids, context=context)
                reversal = expense.rev_ic_move_id.reversal_id
                if reversal:
                    reversal.button_validate()
            expense.state = 'cancelled'
            return res
        else:
            return super(AccountMoveReverse, self).action_reverse(
                cr, uid, ids, context=context)
