# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class LoanBankMOU(models.Model):
    _name = "loan.bank.mou"
    _description = "MOU between Bank and NSTDA"

    name = fields.Char(
        string='MOU Number',
        required=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier (bank)',
        required=True,
        domain=[('supplier', '=', True)],
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank',
        required=True,
        domain="[('partner_id', '=', partner_id)]",
    )
    max_installment = fields.Integer(
        string='Max Installment',
        required=True,
        default=1,
    )
    loan_ratio = fields.Float(
        string='Loan Ratio',
        digits=(16, 12),
        help="Ratio of loan that NSTDA will submit to bank when compare to "
        "full amount. i.e., from 3,000,000 if NSTDA to submit 2,000,000. "
        "Ratio = 2/3 = 0.6666666667",
    )
    product_id = fields.Many2one(
        'product.product',
        string='Loan Product',
        required=True,
    )
    date_begin = fields.Date(
        string='Begin Date',
        required=True,
    )
    date_end = fields.Date(
        string='Date End',
        required=True,
    )
    loan_agreement_ids = fields.One2many(
        'loan.customer.agreement',
        'mou_id',
        string='Loan Agreements',
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'MOU Number must be unique!'),
        ('positive_loan_ratio', 'check(loan_ratio > 0)',
         'Loan ratio must be positive number!'),
        ('positive_loan_ratio', 'check(loan_ratio <= 1)',
         'Loan ratio must not exceed 1!'),
        ('positive_max_installment', 'check(max_installment > 0)',
         'Max installment must be positive number!!'),
    ]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.product_id = self.env.ref('pabi_loan_receivable.product_loan_cd')
        self.bank_id = False


class LoanCustomerAgreement(models.Model):
    _name = "loan.customer.agreement"
    _inherit = ['mail.thread']
    _description = "Loan Agreement between Bank and Customer CC NSTDA"
    _order = "date_begin"

    name = fields.Char(
        string='Loan Agreement Number',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    borrower_partner_id = fields.Many2one(
        'res.partner',
        string='Customer CD',
        domain=[('customer', '=', True)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    mou_id = fields.Many2one(
        'loan.bank.mou',
        string='MOU',
        required=True,
        ondelete='restrict',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer (bank)',
        domain=[('customer', '=', True)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    mou_bank = fields.Many2one(
        'res.bank',
        string="MOU's Bank",
        related='mou_id.bank_id.bank',
        store=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank',
        readonly=True,
        domain="[('partner_id', '!=', False), ('bank', '=', mou_bank)]",
        states={'draft': [('readonly', False)]},
        required=True,
    )
    amount_loan_total = fields.Float(
        string='Total Loan Amount from Bank',
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    amount_receivable = fields.Float(
        string='Loan Amount from NSTDA',
        default=0.0,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    installment = fields.Integer(
        string='Number of Installment',
        default=1,
    )
    date_begin = fields.Date(
        string='Begin Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    monthly_due_type = fields.Selection(
        [('first', 'First day of month'),
         ('last', 'Last day of month'),
         ('specific', 'Specific date (1-28)')],
        string='Payment Due Type',
        default='last',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_specified = fields.Integer(
        string='Specify Date',
        default=1,
        copy=False,
    )
    supplier_invoice_id = fields.Many2one(
        'account.invoice',
        string='Bank Invoice',
        readonly=True,
        copy=False,
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        readonly=True,
        copy=False,
    )
    invoice_plan_ids = fields.One2many(
        'sale.invoice.plan',
        related='sale_id.invoice_plan_ids',
        string='Installment Plan',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('sign', 'Document Signed'),
         ('open', 'Installment Open'),
         ('bank_invoice', 'Bank Invoiced'),
         ('bank_paid', 'Bank Paid'),
         ('done', 'Installment Paid'),
         ('cancel', 'Cancelled')],
        string='Status',
        readonly=True,
        default='draft',
        compute='_compute_state',
        store=True,
    )
    # Fields for state
    signed = fields.Boolean(
        string='Signed',
        default=False,
        readonly=True,
        copy=False,
    )
    cancelled = fields.Boolean(
        string='Cancelled',
        default=False,
        readonly=True,
        copy=False,
    )
    bank_invoice_count = fields.Integer(
        string='Bank Invoice Count',
        compute='_compute_invoice_count',
    )
    installment_invoice_count = fields.Integer(
        string='Installment Invoice Count',
        compute='_compute_invoice_count',
    )
    fy_penalty_rate = fields.Float(
        string='Penalty Rate / Year',
        default=0.0,
    )
    days_grace_period = fields.Integer(
        string='Grace Period (days)',
        default=15,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Payment can be late without penalty if within the grace period",
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        related='section_id.org_id.operating_unit_id',
        readonly=True,
    )
    account_receivable_id = fields.Many2one(
        'account.account',
        string='Account Receivable',
        domain="[('type', '=', 'receivable')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    project = fields.Char(
        string='Project CD',
    )
    _sql_constraints = [
        ('positive_installment', 'check(installment > 0)',
         'Installment must be positive number!'),
        ('positive_fy_penalty_rate', 'check(max_installment >= 0)',
         'Penalty rate must be positive number!!'),
    ]

    @api.onchange('mou_id')
    def _onchange_mou_id(self):
        self.partner_id = self.mou_id.partner_id
        self.bank_id = self.mou_id.bank_id

    @api.multi
    def _compute_invoice_count(self):
        Invoice = self.env['account.invoice']
        for rec in self:
            bank_dom = [('type', 'in', ('in_invoice', 'in_refund')),
                        ('loan_agreement_id', '=', rec.id)]
            install_dom = [('type', 'in', ('out_invoice', 'out_refund')),
                           ('loan_agreement_id', '=', rec.id)]
            rec.bank_invoice_count = \
                len(Invoice.search(bank_dom)._ids)
            rec.installment_invoice_count = \
                len(Invoice.search(install_dom)._ids)

    @api.multi
    @api.depends('signed',
                 'supplier_invoice_id',
                 'supplier_invoice_id.state',
                 'sale_id',
                 'sale_id.state',)
    def _compute_state(self):
        for rec in self:
            state = 'draft'
            if rec.cancelled:
                state = 'cancel'
            if rec.signed:
                state = 'sign'
            if rec.sale_id:
                state = 'open'
            if rec.supplier_invoice_id and \
                    rec.supplier_invoice_id.state not in ('cancel', 'paid',):
                state = 'bank_invoice'
            if rec.supplier_invoice_id and \
                    rec.supplier_invoice_id.state == 'paid':
                state = 'bank_paid'
            if rec.sale_id.state == 'cancel':
                state = 'sign'
            if rec.sale_id and \
                    rec.sale_id.state == 'done':
                state = 'done'
            if rec.cancelled:
                state = 'cancel'
            rec.state = state

    @api.onchange('amount_loan_total')
    def _onchange_amount_loan_total(self):
        amount = self.amount_loan_total * self.mou_id.loan_ratio
        self.amount_receivable = amount

    @api.multi
    @api.constrains('monthly_due_type', 'date_specified')
    def _check_date_specified(self):
        for rec in self:
            if rec.monthly_due_type == 'specific' and \
                    (rec.date_specified < 1 or rec.date_specified > 28):
                raise ValidationError(
                    _('Specified date must be between 1 - 28'))

    @api.multi
    @api.constrains('installment')
    def _check_installment(self):
        for rec in self:
            if rec.installment > rec.mou_id.max_installment:
                raise ValidationError(
                    _('Number of Installment exceed limit in MOU'))

    @api.multi
    @api.constrains('state', 'amount_receivable', 'amount_loan_total',
                    'installment')
    def _check_amount(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                if not rec.amount_receivable or not rec.amount_loan_total:
                    raise ValidationError(_('Loan amount can not be zero!'))
                if rec.installment <= 0:
                    raise ValidationError(
                        _('Installment must be a positive number!'))

    @api.multi
    def open_bank_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        bank_dom = [('type', 'in', ('in_invoice', 'in_refund')),
                    ('loan_agreement_id', '=', self.id)]
        result.update({'domain': bank_dom})
        return result

    @api.multi
    def open_installment_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        install_dom = [('type', 'in', ('out_invoice', 'out_refund')),
                       ('loan_agreement_id', '=', self.id)]
        result.update({'domain': install_dom})
        return result

    @api.multi
    def update_invoice_lines(self, vals):
        InvoiceObj = self.env['account.invoice']
        InvoiceLineObj = self.env['account.invoice.line']
        for loan in self:
            invoice_ids =\
                InvoiceObj.search([('loan_agreement_id', '=', loan.id),
                                   ('state', '=', 'draft')]).ids
            invoice_lines =\
                InvoiceLineObj.search([('invoice_id', 'in', invoice_ids)])
            for line in invoice_lines:
                line.write(vals)

    @api.multi
    def write(self, vals):
        for loan in self:
            if vals.get('section_id', False):
                section_id = vals['section_id']
                loan.update_invoice_lines({'section_id': section_id})
        return super(LoanCustomerAgreement, self).write(vals)

    @api.multi
    def action_sign(self):
        self.write({'signed': True,
                    'cancelled': False})

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state in ('open', 'bank_invoice', 'bank_paid'):
                # Check SO cancelled
                if rec.sale_id and rec.sale_id.state != 'cancel':
                    raise ValidationError(
                        _('Please cancel related sales order first!'))
                # Check bank invoice cancelled
                invoices = self.env['account.invoice'].search([
                    ('loan_agreement_id', '=', rec.id),
                    ('state', '!=', 'cancel')])
                if invoices:
                    raise ValidationError(
                        _('Please cancel all related invoices first!'))
        # Update status
        self.write({'signed': False,
                    'cancelled': True,
                    'state': 'cancel'})

    @api.multi
    def action_cancel_draft(self):
        self.write({'signed': False,
                    'cancelled': False,
                    'state': 'draft'})

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('Cannot delete Loan Agreement which is not '
                      'in state draft or cancelled!'))
        return super(LoanCustomerAgreement, self).unlink()

    @api.multi
    def create_bank_invoice(self, date_invoice):
        for loan in self:
            invoice = loan._create_bank_supplier_invoice_for_loan(date_invoice)
            loan.write({'supplier_invoice_id': invoice.id,
                        'state': 'bank_invoice'})
        return True

    @api.multi
    def create_installment_order(self, date_order):
        self.ensure_one()
        order = self._create_installment_order_for_loan(date_order)
        self.write({'sale_id': order.id,
                    'state': 'open'})
        return order

    # Create Bank Invoice

    @api.model
    def _prepare_inv_header(self, loan, date_invoice):
        Invoice = self.env['account.invoice']
        Journal = self.env['account.journal']
        # Journal
        company_id = self._context.get('company_id',
                                       self.env.user.company_id.id)
        partner_id = loan.bank_id.partner_id.id
        currency_id = self.env.user.company_id.currency_id.id
        journal = Journal.search([('type', '=', 'purchase'),
                                  ('company_id', '=', company_id)],
                                 limit=1)
        if not journal:
            raise ValidationError(
                _("No purchase journal found. Please make sure you "
                  "have a journal with type 'purchase' configured."))
        journal_id = journal[0].id

        res = Invoice.onchange_partner_id(
            'in_invoice', partner_id, date_invoice, payment_term=False,
            partner_bank_id=False, company_id=company_id)['value']

        return {
            'operating_unit_id': loan.operating_unit_id.id,
            'origin': loan.name,
            'comment': False,
            'date_invoice': date_invoice,
            'user_id': self.env.user.id,
            'partner_id': partner_id,
            'account_id': res.get('account_id', False),
            'payment_term': res.get('payment_term', False),
            'fiscal_position': res.get('fiscal_position', False),
            'type': 'in_invoice',
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
            'loan_agreement_id': loan.id,
        }

    @api.model
    def _prepare_inv_line(self, loan, invoice_id, fposition_id):
        InvoiceLine = self.env['account.invoice.line']
        res = InvoiceLine.product_id_change(loan.mou_id.product_id.id, False,
                                            qty=1, name='', type='in_invoice',
                                            partner_id=loan.partner_id.id,
                                            fposition_id=fposition_id)['value']
        return {
            'invoice_id': invoice_id,
            'product_id': loan.mou_id.product_id.id,
            'name': res.get('name', False),
            'account_id': res.get('account_id', False),
            'price_unit': loan.amount_receivable,
            'quantity': 1.0,
            'uos_id': res.get('uos_id', False),
            'section_id': loan.section_id.id,
        }

    @api.multi
    def _create_bank_supplier_invoice_for_loan(self, date_invoice=False):
        self.ensure_one()
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        loan = self
        invoice_vals = self._prepare_inv_header(loan,
                                                date_invoice)
        invoice = Invoice.create(invoice_vals)
        inv_line_data = self._prepare_inv_line(loan, invoice.id,
                                               invoice_vals['fiscal_position'])
        InvoiceLine.create(inv_line_data)
        # Set due date
        res = invoice.onchange_payment_term_date_invoice(
            invoice.payment_term.id, invoice.date_invoice)
        invoice.date_due = res['value']['date_due']
        invoice.button_compute(set_total=True)
        return invoice

    # Create Installment Order

    @api.model
    def _prepare_order_header(self, loan, date_order):
        warehouse_ids = self.env['stock.warehouse'].search(
            [('operating_unit_id', '=', loan.operating_unit_id.id)]).ids
        return {
            'operating_unit_id': loan.operating_unit_id.id,
            'partner_id': loan.partner_id.id,
            'date_order': date_order,
            'client_order_ref': loan.name,
            'use_invoice_plan': True,
            'user_id': self.env.user.id,
            'warehouse_id': warehouse_ids and warehouse_ids[0] or False,
        }

    @api.model
    def _prepare_order_line(self, loan):
        product = loan.mou_id.product_id
        return {
            'product_id': product.id,
            'name': product.name,
            'price_unit': loan.amount_receivable,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 1.0,
            'section_id': loan.section_id.id,
        }

    @api.multi
    def _create_installment_order_for_loan(self, date_order=False):
        self.ensure_one()
        loan = self
        order_vals = self._prepare_order_header(loan, date_order)
        # For payment_term to none, so due date = invoice date in invoices
        order_line_data = self._prepare_order_line(loan)
        order_vals.update({'loan_agreement_id': self.id,
                           'payment_term': False,
                           'order_line': [(0, 0, order_line_data)]})
        order = self.env['sale.order'].\
            with_context(order_type='sale_order').create(order_vals)
        return order
