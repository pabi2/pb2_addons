# -*- coding: utf-8 -*-
from openerp import api, models, fields


class EditDesc(models.TransientModel):
    _name = 'edit.desc'

    name = fields.Char(
        string='Description',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditDesc, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        move_line = self.env[active_model].browse(active_id)
        res['name'] = move_line.name
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        move_line = self.env[active_model].browse(active_id)
        move_line.write({'name': self.name})
        return True
