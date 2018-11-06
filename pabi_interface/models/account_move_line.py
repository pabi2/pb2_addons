# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ref = fields.Char(
        compute='_compute_ref',  # Changed from related field.
        store=True,
        readonly=True,
        help="Note: still preserve related field funciton (can't remove yet)"
    )
    reconcile_move_line_ref = fields.Char(
        string='To Reconcile Ref.',
        readonly=True,
        help="Dummy field, to reference invoice move and payment move."
        "If exists, ref will use this field to display value.",
    )

    @api.multi
    @api.depends('move_id')
    def _compute_ref(self):
        """ If reconcile_move_line_ref exists, use it otherwise fall back """
        for rec in self:
            rec.ref = rec.reconcile_move_line_ref or rec.move_id.ref
        return True

    @api.multi
    def _update_check(self):
        if self._context.get('force_no_update_check', False):
            return True
        return super(AccountMoveLine, self)._update_check()
