# -*- coding: utf-8 -*-
from openerp import api, models, fields


class EditPurchaseLineFY(models.TransientModel):
    _name = 'edit.purchase.order.line.fy'

    fiscalyear_id = fields.Many2one(
        comodel_name='account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(EditPurchaseLineFY, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        line = self.env[active_model].browse(active_id)
        res['fiscalyear_id'] = line.fiscalyear_id.id
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        line = self.env[active_model].browse(active_id)
        line.write({'fiscalyear_id': self.fiscalyear_id.id})
        return True
