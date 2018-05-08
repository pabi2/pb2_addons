# -*- coding: utf-8 -*-
from openerp import models, api


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'employee_expense'
        if vals.get('is_employee_advance', False):
            refer_type = 'employee_advance'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        # --
        fiscalyear_id = self.env['account.fiscalyear'].find()
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        return super(HRExpense, self).create(vals)
