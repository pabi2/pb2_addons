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
