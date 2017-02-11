# -*- coding: utf-8 -*-
from openerp import models, fields, api


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        # compute='_compute_doctype',
        # store=True,
        readonly=True,
    )

    # @api.one
    # @api.depends('is_employee_advance')
    # def _compute_doctype(self):
    #     refer_type = 'employee_expense'
    #     if self.is_employee_advance:
    #         refer_type = 'employee_advance'
    #     doctype = self.env['res.doctype'].search([('refer_type', '=',
    #                                                refer_type)], limit=1)
    #     self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        # Find doctype_id
        refer_type = 'employee_expense'
        if self.is_employee_advance:
            refer_type = 'employee_advance'
        doctype_id = self.env['res.doctype'].search(
            [('refer_type', '=', refer_type)], limit=1).id
        vals.update({'doctype_id': doctype_id})
        # Call super, passing doctype_id
        fiscalyear_id = self.env['account.fiscalyear'].find()
        self = self.with_context(doctype_id=doctype_id,
                                 fiscalyear_id=fiscalyear_id)
        return super(HRExpense, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     new_expense = super(HRExpense, self).create(vals)
    #     if new_expense.doctype_id.sequence_id:
    #         sequence_id = new_expense.doctype_id.sequence_id.id
    #         fiscalyear_id = self.env['account.fiscalyear'].find()
    #         next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
    #             env['ir.sequence'].next_by_id(sequence_id)
    #         new_expense.number = next_number
    #     return new_expense
