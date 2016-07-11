# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp import tools


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    # Add new fk field for each model added
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
    )

    # Add module and fk field
    _models_check = {
        'hr.expense.expense': 'expense_id',
    }

    @api.model
    def create(self, vals):
        for model in self._models_check.keys():
            field = self._models_check[model]
            if vals.get('res_model', False) == model:
                if vals.get('res_id', False):
                    vals[field] = vals.get('res_id')
                if vals.get(field, False):
                    vals['res_id'] = vals.get(field)
        return super(IrAttachment, self).create(vals)

    @api.multi
    def write(self, vals):
        for model in self._models_check.keys():
            field = self._models_check[model]
            if vals.get('res_model', False) == model:
                if vals.get('res_id', False):
                    vals[field] = vals.get('res_id')
                if vals.get(field, False):
                    vals['res_id'] = vals.get(field)
        return super(IrAttachment, self).write(vals)
