# -*- coding: utf-8 -*-

from openerp import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    # Add new fk field for each model added
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
    )
    payment_export_id = fields.Many2one(
        'payment.export',
        string="Payment Export",
    )
    attach_by = fields.Many2one(
        'res.users',
        string="Attach By",
        default=lambda self: self.env.user,
    )

    # Add module and fk field
    _models_check = {
        'hr.expense.expense': 'expense_id',
        'payment.export': 'payment_export_id',
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
