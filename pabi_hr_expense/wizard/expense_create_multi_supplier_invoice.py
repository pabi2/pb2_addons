# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError


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
        string='Supplier Name',
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
        Invoice = self.env['account.invoice']
        Journal = self.env['account.journal']
        # Journal
        journal_id = False
        if expense.journal_id:
            journal_id = expense.journal_id.id
        else:
            journal = Journal.search([('type', '=', 'purchase'),
                                      ('company_id', '=',
                                       expense.company_id.id)])
            if not journal:
                raise UserError(
                    _("No expense journal found. Please make sure you "
                      "have a journal with type 'purchase' configured."))
            journal_id = journal[0].id
        partner = (supplier_info_line.partner_id)
        res = Invoice.onchange_partner_id(
            type, partner.id, expense.date_valid, payment_term=False,
            partner_bank_id=False, company_id=expense.company_id.id)['value']
        return {
            'origin': expense.number,
            'comment': expense.name,
            'date_invoice': expense.date_invoice,
            'user_id': expense.user_id.id,
            'partner_id': partner.id,
            'account_id': res.get('account_id', False),
            'payment_term': res.get('payment_term', False),
            'type': 'in_invoice',
            'fiscal_position': res.get('fiscal_position', False),
            'company_id': expense.company_id.id,
            'currency_id': expense.currency_id.id,
            'journal_id': journal_id,
            'expense_id': expense.id,
        }

    @api.multi
    def create_multi_supplier_invoices(self):
        self.ensure_one()
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        if self.multi_supplier_invoice_line:
            expense_id = self._context.get('expense_id', False)
            expense = self.env['hr.expense.expense'].browse(expense_id)
            alloc = sum([x.amount for x in self.multi_supplier_invoice_line])
            if self.amount_untaxed != alloc:
                raise UserError(_('Allocation amount mismatched.'))
            for supplier_info_line in self.multi_supplier_invoice_line:
                if not supplier_info_line.partner_id:
                    raise UserError(_('Please define supplier.'))
                invoice_vals = self._prepare_inv(supplier_info_line, expense)
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
                if not expense.invoice_id:
                    expense.invoice_id = invoice
                    expense.account_move_id = expense.invoice_id.move_id.id
            expense.write({'state': 'done'})
        return
