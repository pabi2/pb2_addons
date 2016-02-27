# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from openerp.addons import decimal_precision as dp


class HRExpenseExpese(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        [('employee', 'Employee'),
         ('supplier', 'Supplier')],
        string='Pay to',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='employee',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('supplier', '=', True)],
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Supplier Invoice',
        readonly=True,
    )

    @api.model
    def _prepare_inv_line(self, account_id, exp_line):
        return {
            'name': exp_line.name,
            'account_id': account_id,
            'price_unit': exp_line.unit_amount or 0.0,
            'quantity': exp_line.unit_quantity,
            'product_id': exp_line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in exp_line.tax_ids])],
        }

    @api.model
    def _prepare_inv(self, expense):
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
                raise except_orm(
                    _('Error!'),
                    _("No expense journal found. Please make sure you "
                      "have a journal with type 'purchase' configured."))
            journal_id = journal[0].id
        # Partner, account_id, payment_term
        if expense.pay_to == 'employee':
            if not expense.employee_id.address_home_id:
                raise except_orm(
                    _('Error!'),
                    _('The employee must have a home address.'))
            if not expense.employee_id.address_home_id.\
                    property_account_payable:
                raise except_orm(
                    _('Error!'),
                    _('The employee must have a payable account '
                      'set on his home address.'))
        partner = (expense.pay_to == 'employee' and
                   expense.employee_id.address_home_id or
                   expense.partner_id)
        res = Invoice.onchange_partner_id(
            type, partner.id, expense.date_valid, payment_term=False,
            partner_bank_id=False, company_id=expense.company_id.id)['value']
        return {
            'origin': False,
            'comment': expense.name,
            'date_invoice': expense.date_valid,
            'user_id': expense.user_id.id,
            'partner_id': partner.id,
            'account_id': res.get('account_id', False),
            'payment_term': res.get('payment_term', False),
            'type': 'in_invoice',
            'fiscal_position': res.get('fiscal_position', False),
            'company_id': expense.company_id.id,
            'currency_id': expense.currency_id.id,
            'journal_id': journal_id,
        }

    @api.model
    def _choose_account_from_exp_line(self, exp_line, fpos=False):
        FiscalPos = self.env['account.fiscal.position']
        Property = self.env['ir.property']
        account_id = False
        if exp_line.product_id:
            account_id = exp_line.product_id.property_account_expense.id
            if not account_id:
                categ = exp_line.product_id.categ_id
                account_id = categ.property_account_expense_categ.id
            if not account_id:
                raise except_orm(
                    _('Error!'),
                    _('Define an expense account for this '
                      'product: "%s" (id:%d).') %
                    (exp_line.product_id.name, exp_line.product_id.id,))
        else:
            account_id = Property.get('property_account_expense_categ',
                                      'product.category').id
        if fpos:
            fiscal_pos = FiscalPos.browse(fpos)
            account_id = fiscal_pos.map_account(account_id)
        return account_id

    @api.multi
    def _create_supplier_invoice_from_expense(self):
        self.ensure_one()
        inv_lines = []
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        expense = self
        invoice_vals = expense._prepare_inv(expense)
        for exp_line in expense.line_ids:
            account_id = self._choose_account_from_exp_line(
                exp_line, invoice_vals['fiscal_position'])
            inv_line_data = self._prepare_inv_line(account_id, exp_line)
            inv_line = InvoiceLine.create(inv_line_data)
            inv_lines.append(inv_line.id)
        invoice_vals.update({'invoice_line': [(6, 0, inv_lines)]})
        # Create Invoice
        invoice = Invoice.create(invoice_vals)
        invoice.button_compute(set_total=True)
        return invoice

    @api.multi
    def action_move_create(self):
        '''
        Create Supplier Invoice (instead of the old style Journal Entries)
        '''
        for expense in self:
            invoice = expense._create_supplier_invoice_from_expense()
            expense.invoice_id = invoice
            invoice.signal_workflow('invoice_open')
            expense.write({'account_move_id': invoice.move_id.id,
                           'state': 'done'})
        return True


class HRExpenseLine(models.Model):
    _inherit = "hr.expense.line"

    tax_ids = fields.Many2many(
        'account.tax',
        'expense_line_tax_rel',
        'expense_line_id', 'tax_id',
        domain=[('parent_id', '=', False),
                ('type_tax_use', '=', 'purchase')],
        string='Taxes',
    )
    total_amount = fields.Float(
        string='Total',
        digits=dp.get_precision('Account'),
        store=True,
        readonly=True,
        compute='_compute_price',
    )

    @api.one
    @api.depends('unit_amount', 'unit_quantity', 'tax_ids', 'product_id',
                 'expense_id.partner_id', 'expense_id.currency_id')
    def _compute_price(self):
        taxes = self.tax_ids.compute_all(self.unit_amount, self.unit_quantity,
                                         product=self.product_id,
                                         partner=self.expense_id.partner_id)
        self.total_amount = taxes['total_included']
        if self.expense_id:
            currency = self.expense_id.currency_id
            self.total_amount = currency.round(self.total_amount)
