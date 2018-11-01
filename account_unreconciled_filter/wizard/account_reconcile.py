# -*- coding: utf-8 -*-
from openerp import models, api, _


class AccountMoveLineReconcileWriteoff(models.TransientModel):
    _inherit = 'account.move.line.reconcile.writeoff'

    @api.model
    def _open_journal_entry(self, rec_id, context=None):
        context = dict(context or {})
        Reconcile = self.env['account.move.reconcile']
        reconcile = Reconcile.search([('id', '=', rec_id)])
        move_ids = []
        move_ids += reconcile.line_id.mapped('move_id').ids
        move_ids += reconcile.line_partial_ids.mapped('move_id').ids
        context.update({'direct_create': True})  # Ensure chartfield compute
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': unicode([('id', 'in', move_ids)]),
            'context': context,
        }

    @api.v7
    def trans_rec_reconcile(self, cr, uid, ids, context=None):
        """ Overwrite to redirect to JE """
        context = dict(context or {})
        account_move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        account_id = data['writeoff_acc_id'][0]
        context['date_p'] = data['date_p']
        journal_id = data['journal_id'][0]
        context['comment'] = data['comment']
        if data['analytic_id']:
            context['analytic_id'] = data['analytic_id'][0]
        if context['date_p']:
            date = context['date_p']
        ids = period_obj.find(cr, uid, dt=date, context=context)
        if ids:
            period_id = ids[0]
        rec_id = account_move_line_obj.reconcile(
            cr, uid, context['active_ids'], 'manual', account_id,
            period_id, journal_id, context=context)
        return self._open_journal_entry(cr, uid, rec_id, context=context)
