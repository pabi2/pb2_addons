# -*- coding: utf-8 -*-
from openerp import models, api, fields


class AccountAutoReconcile(models.Model):
    _name = 'account.auto.reconcile'

    name = fields.Char(
        string='Code',
        required=True,
        size=50,
        index=True,
        help="Normally use source document number",
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Auto Reconcile Name must be unique'),
    ]

    @api.model
    def get_auto_reconcile_id(self, object):
        name = '%s,%s' % (object._name, object.id)
        auto_reconcile = self.search([('name', '=', name)])
        if auto_reconcile:
            return auto_reconcile.id
        else:
            return self.create({'name': name}).id


class AccountMove(models.Model):
    _inherit = 'account.move'

    auto_reconcile_id = fields.Many2one(
        'account.auto.reconcile',
        string='Auto Reconcile ID',
        copy=False,
        size=20,
        help="To group journal entry for auto reconcilation",
    )

    @api.multi
    def post(self):
        """ For case crate JE manual, to reconcile with another JE """
        res = super(AccountMove, self).post()
        MoveLine = self.env['account.move.line']
        for move in self:
            if move.auto_reconcile_id:
                mlines = MoveLine.search([('auto_reconcile_id', '=',
                                           move.auto_reconcile_id.id)])
                mlines.reconcile_special_account()
        return res

    @api.multi
    def _move_reversal(self, reversal_date,
                       reversal_period_id=False, reversal_journal_id=False,
                       move_prefix=False, move_line_prefix=False):
        """ When do reversal, always set auto_reconcile_id of
            both original and new reversal to original move_id number """
        self.ensure_one()
        reversal_move_id = super(AccountMove, self)._move_reversal(
            reversal_date, reversal_period_id=reversal_period_id,
            reversal_journal_id=reversal_journal_id, move_prefix=move_prefix,
            move_line_prefix=move_line_prefix)
        moves = self.browse([self.id, reversal_move_id])
        Auto = self.env['account.auto.reconcile']
        auto_id = Auto.get_auto_reconcile_id(self)
        moves.write({'auto_reconcile_id': auto_id})
        return reversal_move_id
