# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class ExpenseCreateMultiSupplierInvoiceLine(models.TransientModel):
    _name = "expense.create.multi.supplier.invoice.line"

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
    )
    partner_name = fields.Char(
        string='Supplier Info.',
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
    )
    multi_supplier_invoice_id = fields.Many2one(
        'expense.create.multi.supplier.invoice',
        string='Multi Supplier Invoice',
    )


class ExpenseCreateMultiSupplierInvoice(models.TransientModel):
    _name = "expense.create.multi.supplier.invoice"

    amount_untaxed = fields.Float(
        string='Amount Untaxed',
        readonly=True,
    )
    multi_supplier_invoice_line = fields.One2many(
        'expense.create.multi.supplier.invoice.line',
        'multi_supplier_invoice_id',
        string='Multi Supplier Invoice Lines',
    )

    @api.model
    def _prepare_inv(self, supplier_info_line, expense):
        return self.env['hr.expense.expense'].\
            _prepare_inv_header(supplier_info_line.partner_id.id, expense)

    @api.multi
    def create_multi_supplier_invoices(self):
        self.ensure_one()
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        if not self.multi_supplier_invoice_line:
            raise ValidationError(_('No person in the Supplier List table!'))
        else:
            expense_id = self._context.get('expense_id', False)
            date_invoice = self._context.get('date_invoice', False)
            expense = self.env['hr.expense.expense'].browse(expense_id)
            alloc = sum([x.amount for x in self.multi_supplier_invoice_line])
            if self.amount_untaxed != alloc:
                raise ValidationError(_('Allocation amount mismatched.'))
            for supplier_info_line in self.multi_supplier_invoice_line:
                if not supplier_info_line.partner_id:
                    raise ValidationError(_('Please define supplier.'))
                # Invoice Head
                invoice_vals = self._prepare_inv(supplier_info_line, expense)
                invoice_vals['date_invoice'] = date_invoice
                # Invoice Line
                inv_lines = []
                exp_line = expense.line_ids[0]
                account_id = expense._choose_account_from_exp_line(
                    exp_line, invoice_vals['fiscal_position'])
                inv_line_data = expense._prepare_inv_line(account_id,
                                                          exp_line)
                inv_line_data['quantity'] = 1.0  # Always set back to 1
                inv_line_data['price_unit'] = supplier_info_line.amount
                inv_line = InvoiceLine.create(inv_line_data)
                inv_lines.append(inv_line.id)
                exp_line.write({'invoice_line_ids': [(4, inv_line.id)]})
                invoice_vals.update({'invoice_line': [(6, 0, inv_lines)]})
                # Create Invoice
                invoice = Invoice.create(invoice_vals)
                invoice.button_compute(set_total=True)
                invoice.amount_expense_request = invoice.amount_total
                if not expense.invoice_id:
                    expense.invoice_id = invoice
                    expense.account_move_id = expense.invoice_id.move_id.id
#             expense.write({'state': 'done'})
            expense.signal_workflow('done')
        return
