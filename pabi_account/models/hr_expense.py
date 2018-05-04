# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def _prepare_pettycash_inv_lines(self, expense, pettycash):
        pettycash_line = super(HRExpense, self).\
            _prepare_pettycash_inv_lines(expense, pettycash)
        pettycash_line.update(
            {'section_id': pettycash.partner_id.employee_id.section_id.id})
        return pettycash_line


class HRExpenseClearing(models.Model):
    _inherit = 'hr.expense.clearing'

    validate_user_id = fields.Many2one(
        'res.users',
        string='Validated by',
    )

    def _sql_select_1(self):
        sql_select = super(HRExpenseClearing, self)._sql_select_1()
        return sql_select + ', null as validate_user_id'

    def _sql_select_2(self):
        sql_select = super(HRExpenseClearing, self)._sql_select_2()
        return sql_select + ', validate_user_id'

    def _sql_select_3(self):
        sql_select = super(HRExpenseClearing, self)._sql_select_3()
        return sql_select + ', ai.validate_user_id'
