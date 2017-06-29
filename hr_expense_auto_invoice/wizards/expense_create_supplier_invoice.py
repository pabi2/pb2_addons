# -*- coding: utf-8 -*-
from openerp import api, models, fields


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _name = "expense.create.supplier.invoice"

    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
    )
    pay_to = fields.Selection(
        [('employee', 'Employee'),
         ('supplier', 'Supplier')],
        string='Pay Type',
        readonly=True,
    )

    @api.model
    def default_get(self, field_list):
        res = super(ExpenseCreateSupplierInvoice, self).default_get(field_list)
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id'))
        res['pay_to'] = expense.pay_to
        return res

    @api.multi
    def action_create_supplier_invoice(self):
        self.ensure_one()
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id', False))
        expense.date_invoice = self.date_invoice
        expense.partner_id = self.partner_id
        expense.signal_workflow('done')
