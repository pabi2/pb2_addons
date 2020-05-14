# -*- coding: utf-8 -*-
from openerp.osv import fields, orm
from openerp import models, api


class AccountAccount(orm.Model):
    _inherit = 'account.account'

    _columns = {
        'centralized': fields.boolean(
            'Centralized',
            help="If flagged, no details will be displayed in "
                 "the General Ledger report (the webkit one only), "
                 "only centralized amounts per period."),
    }
    _defaults = {
        'centralized': False,
    }


class AccountMoveReconcile(models.Model):
    _inherit = 'account.move.reconcile'

    @api.multi
    def _get_percent_unpaid(self, date_stop):
        MoveLine = self.env['account.move.line']
        Account = self.env['account.account']
        move_lines = MoveLine.sudo().search_read(
            [('date', '<=', date_stop),
             '|', ('reconcile_id', 'in', self.ids),
             ('reconcile_partial_id', 'in', self.ids)],
            ['reconcile_ref', 'debit', 'credit', 'account_id'])
        vals = []
        acc = []
        for rec in self:
            # IF Reconcile ID = None that's mean percent_unpaid = 100%
            if not rec.id:
                vals.append(1.0)
                continue
            total_debit = 0.0
            total_credit = 0.0
            percent_unpaid = 0.0
            lines = filter(
                lambda l: l['reconcile_ref'] == rec.name, move_lines
            )
            total_debit = sum([x['debit'] for x in lines])
            total_credit = sum([x['credit'] for x in lines])
            account_id = lines[0].get('account_id')
            account = Account.browse(account_id[0])
            if account.type == 'receivable':
                if total_debit != 0 and total_debit > total_credit:
                    percent_unpaid = (total_debit-total_credit)/total_debit
            elif account.type == 'payable':
                if total_credit != 0 and total_credit > total_debit:
                    percent_unpaid = (total_credit-total_debit)/total_credit
            vals.append(percent_unpaid)
            acc.append(account.type)
        return vals, acc
