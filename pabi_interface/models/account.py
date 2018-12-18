# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    system_id = fields.Many2one(
        'interface.system',
        string='Interface System',
        ondelete='restrict',
        help="System where this interface transaction is being called",
    )

    @api.model
    def create(self, vals):
        if not vals.get('system_id', False):
            default_pabi2 = self.env.ref('pabi_interface.system_pabi2')
            vals.update({
                'system_id': default_pabi2.id})
        return super(AccountMove, self).create(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    system_id = fields.Many2one(
        'interface.system',
        string='Interface System',
        ondelete='restrict',
        related='move_id.system_id',
        store=True,
        help="System where this interface transaction is being called",
    )


class AccountMoveReconcile(models.Model):
    _inherit = 'account.move.reconcile'

    @api.multi
    def reconcile_partial_check(self, type='auto'):
        """ Only in IA document, we found problem with total,
        so we use abs(total) < 0.0001 """
        total = 0.0
        for rec in self:
            for line in rec.line_partial_ids:
                if line.account_id.currency_id:
                    total += line.amount_currency
                else:
                    total += (line.debit or 0.0) - (line.credit or 0.0)
        if not total or abs(total) < 0.00001:
            rec.line_partial_ids.write({'reconcile_id': rec.id,
                                        'reconcile_partial_id': False}, )
        return True
