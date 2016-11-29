# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    system_origin_id = fields.Many2one(
        'system.origin',
        string='System Origin',
        ondelete='restrict',
        requried=True,
        default=lambda s: s.env.ref('pabi_interface.system_origin_pabi2'),
        help="System Origin where this interface transaction is being called",
    )


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
