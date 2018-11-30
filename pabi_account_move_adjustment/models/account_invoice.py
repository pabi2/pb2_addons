# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    adjust_move_id = fields.Many2one(
        'account.move',
        string='Adjustment Journal Entry',
        readonly=True,
        index=True,
        ondelete='set null',
        copy=False,
        help="Obsoluted field, use adjust_move_ids instead",
    )
    adjust_move_ids = fields.Many2many(
        'account.move',
        'account_invoice_move_rel',
        'invoice_id', 'move_id',
        string='Adjustment Journal Entries',
        readonly=True,
        ondelete='set null',
        copy=False,
    )
    adjust_move_count = fields.Integer(
        string='Adjust Move Count',
        compute='_compute_assset_count',
    )

    @api.multi
    def _compute_assset_count(self):
        for rec in self:
            adjust_move_ids = rec.adjust_move_ids.ids
            if rec.adjust_move_id:  # backward compatability
                adjust_move_ids.append(rec.adjust_move_id.id)
            rec.adjust_move_count = len(adjust_move_ids)
        return True

    @api.multi
    def action_open_adjust_journal(self):
        self.ensure_one()
        action = self.env.ref('pabi_account_move_adjustment.'
                              'action_journal_adjust_no_budget')
        if not action:
            raise ValidationError(_('No Action'))
        res = action.read([])[0]  # backward compatability
        adjust_move_ids = self.adjust_move_ids.ids + [self.adjust_move_id.id]
        res['domain'] = [('id', 'in', adjust_move_ids)]
        return res
