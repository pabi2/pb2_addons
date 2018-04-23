# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class AccountMoveLine(orm.Model):

    """Overriding Account move line in order to add last_rec_date.
    Last rec date is the date of the last reconciliation (full or partial)
    account move line"""
    _inherit = 'account.move.line'

    def _get_move_line_from_line_rec(self, cr, uid, ids, context=None):
        moves = []
        for reconcile in self.pool['account.move.reconcile'].browse(
                cr, uid, ids, context=context):
            for move_line in reconcile.line_partial_ids:
                moves.append(move_line.id)
            for move_line in reconcile.line_id:
                moves.append(move_line.id)
        return list(set(moves))

    def _get_last_rec_date(self, cursor, uid, ids, name, args, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        res = {}
        for line in self.browse(cursor, uid, ids, context):
            res[line.id] = {'last_rec_date': False}
            rec = line.reconcile_id or line.reconcile_partial_id or False
            if rec:
                # we use cursor in order to gain some perfs.
                # also, important point: LIMIT 1 is not used due to
                # performance issues when in conjonction with "OR"
                # (one backwards index scan instead of 2 scans and a sort)
                cursor.execute('SELECT date from account_move_line'
                               ' WHERE reconcile_id = %s'
                               ' OR reconcile_partial_id = %s'
                               ' ORDER BY date DESC',
                               (rec.id, rec.id))
                res_set = cursor.fetchone()
                if res_set:
                    res[line.id] = {'last_rec_date': res_set[0]}
        return res

    _columns = {
        'last_rec_date': fields.function(
            _get_last_rec_date,
            method=True,
            string='Last reconciliation date',
            store={'account.move.line': (lambda self, cr, uid, ids, c={}: ids,
                                         ['date'], 20),
                   'account.move.reconcile': (_get_move_line_from_line_rec,
                                              None, 20)},
            type='date',
            multi='all',
            help="the date of the last reconciliation (full or partial) \
                  account move line"),
    }
