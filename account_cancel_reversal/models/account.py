# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def _switch_dr_cr(self):
        self.ensure_one()
        for line in self.line_id:
            line.write({'credit': line.debit, 'debit': line.credit})

    @api.model
    def _reconcile_voided_entry(self, move_ids):
        AccountMoveLine = self.env['account.move.line']
        Period = self.env['account.period']
        date = fields.Date.context_today(self)
        periods = Period.find(dt=date)
        period_id = periods and periods[0].id or False
        # Getting move_line_ids of the voided documents.
        print self._ids
        move_lines = \
            AccountMoveLine.search([('account_id.reconcile', '=', True),
                                    ('reconcile_id', '=', False),
                                    ('move_id', 'in', move_ids)])
        print move_lines
        move_lines.reconcile('manual', False, period_id, False)
