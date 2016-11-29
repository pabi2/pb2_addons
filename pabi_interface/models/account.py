# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    system_origin_id = fields.Many2one(
        'system.origin',
        string='System Origin',
        ondelete='restrict',
        help="System Origin where this interface transaction is being called",
    )

    @api.model
    def create(self, vals):
        if not vals.get('system_origin_id', False):
            default_pabi2 = self.env.ref('pabi_interface.system_origin_pabi2')
            vals.update({
                'system_origin_id': default_pabi2.id})
        return super(AccountMove, self).create(vals)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    system_origin_id = fields.Many2one(
        'system.origin',
        string='System Origin',
        ondelete='restrict',
        related='move_id.system_origin_id',
        store=True,
        help="System Origin where this interface transaction is being called",
    )
