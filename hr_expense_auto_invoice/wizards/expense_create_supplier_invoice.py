# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ExpenseCreateSupplierInvoice(models.TransientModel):
    _name = "expense.create.supplier.invoice"

    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Date.today(),
    )

    @api.multi
    def action_create_supplier_invoice(self):
        self.ensure_one()
        Expense = self.env['hr.expense.expense']
        expense = Expense.browse(self._context.get('active_id', False))
        expense.date_invoice = self.date_invoice
        expense.signal_workflow('done')
