# -*- coding: utf-8 -*-
# © 2016 Kitti U.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError


class ExpenseCreateMultiSupplierInvoiceLine(models.TransientModel):
    _name = "expense.create.multi.supplier.invoice.line"

    employee_id = fields.Many2one(
        'hr.employee',
        'Employee'
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Supplier',
    )
    partner_name = fields.Char('Supplier Name', )
    taxid = fields.Char('Tax ID', )
#     amount = fields.Float('Amount', )
    multi_supplier_invoice_id = fields.Many2one(
        'expense.create.multi.supplier.invoice',
        'Multi Supplier Invoice',
    )


class ExpenseCreateMultiSupplierInvoice(models.TransientModel):
    _name = "expense.create.multi.supplier.invoice"

    multi_supplier_invoice_line = fields.One2many(
        'expense.create.multi.supplier.invoice.line',
        'multi_supplier_invoice_id',
        'Multi Supplier Invoice Lines'
    )
#     total_amount = fields.Float(
#         compute='_compute_total_amount',
#         string="Total Amount",
#         store=True,
#         readonly=True,
#     )
# 
#     @api.depends('multi_supplier_invoice_line',
#                  'multi_supplier_invoice_line.amount')
#     def _compute_total_amount(self):
#         for record in self:
#             for line in record.multi_supplier_invoice_line:
#                 record.total_amount += line.amount

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
        first_invoice = True
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        if self.multi_supplier_invoice_line:
            expense_id = self._context.get('expense_id', False)
            expense = self.env['hr.expense.expense'].browse(expense_id)
            for supplier_info_line in self.multi_supplier_invoice_line:
                if not supplier_info_line.partner_id:
                    raise UserError(_('Warning'),
                                  _('Please define supplier.'))
#                 if self.total_amount != expense.amount:
#                     raise UserError(_('Warning'),
#                                     _('Amount mismatched.'))
                invoice_vals = self._prepare_inv(supplier_info_line, expense)
                inv_lines = []
                for exp_line in expense.line_ids:
                    account_id = expense._choose_account_from_exp_line(
                        exp_line, invoice_vals['fiscal_position'])
                    inv_line_data = expense._prepare_inv_line(account_id, exp_line)
                    if not first_invoice:
                        inv_line_data['quantity'] = 0.0

                    inv_line = InvoiceLine.create(inv_line_data)
                    inv_lines.append(inv_line.id)
                    exp_line.write({'invoice_line_ids': [(4, inv_line.id)]})
                invoice_vals.update({'invoice_line': [(6, 0, inv_lines)]})
#                 # Create Invoice
                invoice = Invoice.create(invoice_vals)
                first_invoice = False
                invoice.button_compute(set_total=True)
                if not expense.invoice_id:
                    expense.invoice_id = invoice
                    expense.account_move_id = expense.invoice_id.move_id.id
                # invoice.signal_workflow('invoice_open')
            expense.write({'state': 'done'})
        return
