# -*- coding: utf-8 -*-
from openerp import models, api


class HRSalaryExpense(models.Model):
    _inherit = 'hr.salary.expense'

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'salary_expense'
        doctype = self.env['res.doctype'].get_doctype(refer_type)
        # --
        fiscalyear_id = self.env['account.fiscalyear'].find()
        self = self.with_context(doctype_id=doctype.id,
                                 fiscalyear_id=fiscalyear_id)
        return super(HRSalaryExpense, self).create(vals)

    @api.multi
    def _prepare_move(self):
        self.ensure_one()
        vals = super(HRSalaryExpense, self)._prepare_move()
        vals.update({'name': self.number})
        return vals
