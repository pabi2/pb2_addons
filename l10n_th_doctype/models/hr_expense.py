# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


_DOCTYPE = {'quotation': 'purchase_quotation',
            'purchase_order': 'purchase_order'}


class HRExpense(models.Model):
    _inherit = 'hr.expense.expense'

    doctype_id = fields.Many2one(
        'res.doctype',
        string='Doctype',
        compute='_compute_doctype',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('is_employee_advance')
    def _compute_doctype(self):
        refer_type = 'employee_expense'
        if self.is_employee_advance:
            refer_type = 'employee_advance'
        doctype = self.env['res.doctype'].search([('refer_type', '=',
                                                   refer_type)], limit=1)
        self.doctype_id = doctype.id

    @api.model
    def create(self, vals):
        new_expense = super(HRExpense, self).create(vals)
        if new_expense.doctype_id.sequence_id:
            sequence_id = new_expense.doctype_id.sequence_id.id
            fiscalyear_id = self.env['account.fiscalyear'].find()
            next_number = self.with_context(fiscalyear_id=fiscalyear_id).\
                env['ir.sequence'].next_by_id(sequence_id)
            new_expense.number = next_number
        return new_expense
