# -*- coding: utf-8 -*-
from openerp import models, fields, api


class MoveOpenUnreconciledItems(models.TransientModel):
    _name = 'move.open.unreconciled.items'

    move_line_ref = fields.Char(
        string='Item Ref',
        size=100,
    )
    account_move_name = fields.Char(
        string='Journal Item Desc.',
        size=100,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account Code',
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Journal Entries',
    )

    @api.multi
    def action_open_unreconciled_items(self):
        self.ensure_one()
        action = self.env.ref(
            'account_unreconciled_filter.action_account_move_open_items')
        result = action.read()[0]
        move = self.env['account.move'].browse(self._context.get('active_id'))
        # Serach for unrconcieled item with account = reconile
        MoveLine = self.env['account.move.line']
        domain = [('reconcile_id', '=', False),
                  ('account_id.reconcile', '=', True)]
        src_ml_ids = MoveLine.search(domain + [('move_id', '=', move.id)]).ids
        # Item to reconcile with
        trg_ml_ids = []
        if self.move_line_ref:
            trg_ml_ids += MoveLine.search(
                domain + [('ref', '=', self.move_line_ref)]).ids
        if self.account_move_name:
            trg_ml_ids += MoveLine.search(
                domain + [('name', '=', self.account_move_name)]).ids
        if self.account_id:
            trg_ml_ids += MoveLine.search(
                domain + [('account_id', '=', self.account_id.id)]).ids
        if self.move_ids:
            trg_ml_ids += MoveLine.search(
                domain + [('move_id', 'in', self.move_ids.ids)]).ids
        result.update({'domain': [('id', 'in', src_ml_ids + trg_ml_ids)]})
        return result
