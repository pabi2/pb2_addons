# -*- coding: utf-8 -*-
from openerp import models, api


class AccountOpenClosedFiscalyear(models.TransientModel):
    _inherit = 'account.open.closed.fiscalyear'

    @api.multi
    def remove_entries(self):
        self.ensure_one()
        move_obj = self.env['account.move']
        period_journal = self.fyear_id.end_journal_period_id or False
        ids_move = move_obj.search([
            ('journal_id', '=', period_journal.journal_id.id),
            ('period_id', '=', period_journal.period_id.id)])
        if ids_move:
            # Disable Trigger
            self._cr.execute(
                'alter table account_move_line disable trigger all'
            )
            self._cr.execute(
                'alter table account_move disable trigger all'
            )
            # --
            self._cr.execute(
                'delete from account_move_line where move_id IN (%s)',
                (ids_move.ids)
            )

            super(AccountOpenClosedFiscalyear, self).remove_entries()
            # Enable Trigger
            self._cr.execute(
                "alter table account_move_line enable trigger all"
            )
            self._cr.execute(
                "alter table account_move enable trigger all"
            )
        return {'type': 'ir.actions.act_window_close'}
