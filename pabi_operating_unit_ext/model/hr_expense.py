# -*- coding: utf-8 -*-
from openerp import fields, models, api


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )

    @api.model
    def _prepare_inv(self, expense):
        res = super(HrExpenseExpense, self)._prepare_inv(expense)
        res.update({'operating_unit_id': expense.operating_unit_id.id})
        return res
