# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountMoveReverse(models.TransientModel):
    _inherit = 'account.move.reverse'

    move_prefix = fields.Char(
        default=lambda self: self._default_move_prefix(),
    )

    @api.model
    def view_init(self, fields_list):
        """ Allow only Adjustment Journal to be reversed """
        res_model = self._context.get('active_model', False)
        res_id = self._context.get('active_id', False)
        move = self.env[res_model].browse(res_id)
        if move.doctype not in ('adjustment', 'interface_account'):
            raise ValidationError(
                _('No direct reverse allowed for non adjustment doctype!\n'
                  'You should make reverse on source document.'))

    @api.model
    def _default_move_prefix(self):
        move_ids = self._context.get('active_ids', False)
        if move_ids and len(move_ids) == 1:
            move = self.env['account.move'].browse(move_ids[0])
            return '%s - ' % move.name
