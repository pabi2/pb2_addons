# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
