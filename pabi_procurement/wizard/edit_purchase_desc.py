# -*- coding: utf-8 -*-
from openerp import api, models, fields


class EditPurchaseDesc(models.TransientModel):
    _name = 'edit.purchase.desc'

    name = fields.Char(
        string='Description',
        required=True,
        size=500,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditPurchaseDesc, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        purchase_line = self.env[active_model].browse(active_id)
        res['name'] = purchase_line.name
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        purchase_line = self.env[active_model].browse(active_id)
        purchase_line.write({'name': self.name})
        return True
