# -*- coding: utf-8 -*-
from itertools import groupby
from operator import itemgetter
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.addons import decimal_precision as dp


class HRExpenseExpese(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        [('employee', 'Employee'),
         ('supplier', 'Supplier')],
        string='Pay Type',
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
        copy=False,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Supplier Invoice',
        readonly=True,
        copy=False,
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        readonly=True,
        copy=False,
    )
    journal_id = fields.Many2one(
        readonly=True,
        copy=False,
    )
    account_move_id = fields.Many2one(
        readonly=True,
        copy=False,
        ondelete='set null',
    )
    invoice_ids = fields.One2many(
        'account.invoice',
        'expense_id',
        string='Invoices',
        copy=False,
    )
    is_invoiced = fields.Boolean(
        compute='_compute_invoiced',
        string='Invoiced',
    )
    to_invoice_amount = fields.Float(
        compute='_compute_invoiced',
        string='Amount To Invoice ',
        readonly=True,
    )

    @api.multi
    @api.depends('invoice_ids', 'invoice_ids.state')
    def _compute_invoiced(self):
        for expense in self:
            invoice_amount = 0.0
            for invoice in expense.invoice_ids:
                if invoice.state != 'cancel':
                    invoice_amount += invoice.amount_total
            if invoice_amount != expense.amount:
                expense.is_invoiced = False
                expense.to_invoice_amount = expense.amount - invoice_amount
            else:
                expense.is_invoiced = True
                expense.to_invoice_amount = 0.0
            if expense.is_advance_clearing or\
                    expense.is_employee_advance:
                expense.is_invoiced = True
                expense.to_invoice_amount = 0.0

    @api.model
    def _prepare_inv_line(self, account_id, exp_line):
        return {
            'name': exp_line.name,
            'account_id': account_id,
            'price_unit': exp_line.unit_amount or 0.0,
            'quantity': exp_line.unit_quantity,
            'product_id': exp_line.product_id.id or False,
        }

    @api.model
    def _prepare_inv_header(self, partner_id, expense):
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

        res = Invoice.onchange_partner_id(
            type, partner_id, expense.date_valid, payment_term=False,
            partner_bank_id=False, company_id=expense.company_id.id)['value']

        invoice_ref_id = False
        if expense.invoice_ids:
            if any([invoice.state == 'cancel' for
                    invoice in
                    expense.invoice_ids]):
                invoice_ids = expense.invoice_ids.ids
                invoice_ref_id = invoice_ids[-1]

        return {
            'origin': expense.number,
            'comment': expense.name,
            'date_invoice': expense.date_invoice,
            'user_id': expense.user_id.id,
            'partner_id': partner_id,
            'account_id': res.get('account_id', False),
            'payment_term': res.get('payment_term', False),
            'type': 'in_invoice',
            'fiscal_position': res.get('fiscal_position', False),
            'company_id': expense.company_id.id,
            'currency_id': expense.currency_id.id,
            'journal_id': journal_id,
            'expense_id': expense.id,
            'invoice_ref_id': invoice_ref_id,
        }

    @api.model
    def _prepare_inv(self, expense):
        # Partner, account_id, payment_term
        if expense.pay_to == 'employee':
            if not expense.employee_id.user_id.partner_id:
                raise UserError(
                    _('The employee must have a valid user in system'))
            if not expense.employee_id.user_id.partner_id.\
                    property_account_payable:
                raise UserError(
                    _('The employee must have a payable account '
                      'set on referred user/partner.'))
        partner = (expense.pay_to == 'employee' and
                   expense.employee_id.user_id.partner_id or
                   expense.partner_id)
        return self._prepare_inv_header(partner.id, expense)

    @api.model
    def _choose_account_from_exp_line(self, exp_line, fpos=False):
        FiscalPos = self.env['account.fiscal.position']
        account_id = False
        if exp_line.product_id:
            account_id = exp_line.product_id.property_account_expense.id
            if not account_id:
                categ = exp_line.product_id.categ_id
                account_id = categ.property_account_expense_categ.id
            if not account_id:
                raise UserError(
                    _('Define an expense account for this '
                      'product: "%s" (id:%d).') %
                    (exp_line.product_id.name, exp_line.product_id.id,))
        else:
            account_id = exp_line._get_non_product_account_id()
        if fpos:
            fiscal_pos = FiscalPos.browse(fpos)
            account_id = fiscal_pos.map_account(account_id)
        return account_id

    @api.model
    def merge_invoice_line(self, input_data, group_keys, sum_keys, str_keys):
        grouper = itemgetter(*group_keys)
        result = []
        for key, grp in groupby(sorted(input_data, key=grouper), grouper):
            temp_dict = dict(zip(group_keys, key))
            for value in sum_keys:
                temp_dict[value] = 0.0
            for value in str_keys:
                temp_dict[value] = ''
            for item in grp:
                for value in sum_keys:
                    temp_dict[value] += item.get(value, 0.0)
                for value in str_keys:
                    word = item.get(value, '')
                    if len(word) > 0:
                        temp_dict[value] += \
                            len(temp_dict[value]) and ',\n' + word or word
            result.append(temp_dict)
        return result

    @api.multi
    def _create_supplier_invoice_from_expense(self, merge_line=False):
        self.ensure_one()
        inv_lines = []
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        expense = self
        invoice_vals = self._prepare_inv(expense)
        inv_line_datas = []
        for exp_line in expense.line_ids:
            account_id = self._choose_account_from_exp_line(
                exp_line, invoice_vals['fiscal_position'])
            inv_line_datas.append(self._prepare_inv_line(account_id, exp_line))
        if merge_line and inv_line_datas:
            keys = inv_line_datas[0].keys()
            sum_keys = ['quantity']  # This field will be summed
            str_keys = ['name']  # This field will be concatenate
            group_keys = list(set(keys) - set(sum_keys) - set(str_keys))
            inv_line_datas = \
                self.merge_invoice_line(inv_line_datas, group_keys,
                                        sum_keys, str_keys)
        for inv_line_data in inv_line_datas:
            inv_line = InvoiceLine.create(inv_line_data)
            inv_lines.append(inv_line.id)
        invoice_vals.update({'invoice_line': [(6, 0, inv_lines)]})
        # Create Invoice
        invoice = Invoice.create(invoice_vals)
        # Set due date
        res = invoice.onchange_payment_term_date_invoice(
            invoice.payment_term.id, invoice.date_invoice)
        invoice.date_due = res['value']['date_due']
        invoice.button_compute(set_total=True)
        return invoice

    @api.multi
    def expense_confirm(self):
        for expense in self:
            if 'is_advance_clearing' not in expense:
                if expense.amount <= 0.0:
                    raise UserError(_('This expense have no lines,\
                    or all lines with zero amount.'))
        return super(HRExpenseExpese, self).expense_confirm()

    @api.model
    def _is_valid_for_invoice(self):
        # HOOK
        return True

    @api.multi
    def action_move_create(self):
        '''
        Create Supplier Invoice (instead of the old style Journal Entries)
        '''
        for expense in self:
            if expense._is_valid_for_invoice():
                if not expense.invoice_id:
                    invoice = expense._create_supplier_invoice_from_expense()
                    expense.invoice_id = invoice
                expense.write({
                    'account_move_id': expense.invoice_id.move_id.id,
                    'state': 'done'
                })
        return True

    @api.multi
    def action_view_move(self):
        '''
        Override this method to open Invoice instead of move lines
        '''
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        invoice_ids = self.env['account.invoice'].\
            search([('expense_id', '=', self.id)])
        result.update({'domain': [('id', 'in', invoice_ids.ids)],
                       'res_id': self.invoice_id.id})
        if len(invoice_ids.ids) > 1:
            result.update({'views': [(False, u'tree'), (False, u'form')]})
        else:
            result.update({'views': [(False, u'form'), (False, u'tree')]})
        return result

    @api.multi
    def action_paid(self):
        for expense in self:
            expense.write({'state': 'paid'})
        return True


class HRExpenseLine(models.Model):
    _inherit = "hr.expense.line"

    expense_state = fields.Selection(
        [('draft', 'New'),
         ('cancelled', 'Refused'),
         ('confirm', 'Waiting Approval'),
         ('accepted', 'Approved'),
         ('done', 'Waiting Payment'),
         ('paid', 'Paid'),
         ],
        string='Expense state',
        readonly=True,
        related='expense_id.state',
        store=True,
    )
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
    invoice_line_ids = fields.Many2many(
        'account.invoice.line',
        'expense_line_invoice_line_rel',
        'expense_line_id',
        'invoice_line_id',
        readonly=True,
        copy=False,
    )
    open_invoiced_qty = fields.Float(
        string='Invoiced Quantity',
        digits=(12, 6),
        compute='_compute_open_invoiced_qty',
        store=True,
        copy=False,
        default=0.0,
        help="This field calculate invoiced quantity at line level. "
        "Will be used to calculate committed budget",
    )

    @api.depends('invoice_line_ids.invoice_id.state')
    def _compute_open_invoiced_qty(self):
        Uom = self.env['product.uom']
        for expense_line in self:
            open_invoiced_qty = 0.0
            for invoice_line in expense_line.invoice_line_ids:
                invoice = invoice_line.invoice_id
                if invoice.state and invoice.state not in ['draft', 'cancel']:
                    # Invoiced Qty in PO Line's UOM
                    open_invoiced_qty += \
                        Uom._compute_qty(invoice_line.uos_id.id,
                                         invoice_line.quantity,
                                         expense_line.uom_id.id)
            expense_line.open_invoiced_qty = min(expense_line.unit_quantity,
                                                 open_invoiced_qty)

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

    @api.multi
    def onchange_product_id(self, product_id):
        res = super(HRExpenseLine, self).onchange_product_id(product_id)
        if product_id:
            product = self.env['product.product'].browse(product_id)
            taxes = [tax.id for tax in product.supplier_taxes_id]
            res['value']['tax_ids'] = [(6, 0, taxes)]
        return res

    @api.model
    def _get_non_product_account_id(self):
        Property = self.env['ir.property']
        return Property.get('property_account_expense_categ',
                            'product.category').id
