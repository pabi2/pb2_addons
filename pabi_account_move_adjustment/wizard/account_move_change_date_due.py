# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountMoveChangeDateDue(models.TransientModel):
    _name = "account.move.change.date.due"

    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        default=lambda self: self._context.get('active_id', False),
    )
    date_due = fields.Date(
        string='Due Date',
        required=True,
    )
    reason = fields.Char(
        string='Reason',
        required=True,
    )

    @api.multi
    def change_account_move_date_due(self):
        self.ensure_one()
        if self.date_due:
            history_obj = self.env['account.move.due.history']
            move_id = self._context.get('active_id', False)
            move = self.env['account.move'].browse(move_id)
            date_old_due = self.move_id.date_due
            move.line_id.filtered('date_maturity').\
                write({'date_maturity': self.date_due})
            if self.date_due:
                history_obj.create({
                    'move_id': self.move_id.id,
                    'date_old_due': date_old_due,
                    'date_due': self.date_due,
                    'reason': self.reason,
                })
