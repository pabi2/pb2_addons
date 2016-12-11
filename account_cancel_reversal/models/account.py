# -*- coding: utf-8 -*-
from openerp import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def _switch_dr_cr(self):
        self.ensure_one()
        if self.state == 'posted':
            self.button_cancel()
        for line in self.line_id:
            line.write({'credit': line.debit, 'debit': line.credit})
        self.button_validate()

    @api.model
    def _reconcile_voided_entry(self, move_ids):
        AccountMoveLine = self.env['account.move.line']
        # Getting move_line_ids of the voided documents.
        move_lines = \
            AccountMoveLine.search([('account_id.reconcile', '=', True),
                                    ('reconcile_id', '=', False),
                                    ('move_id', 'in', move_ids)])
        if move_lines:
            move_lines.reconcile('manual')
