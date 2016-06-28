# -*- coding: utf-8 -*-
from lxml import etree
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp


class HRExpenseLine(models.Model):
    _inherit = "hr.expense.line"

    is_advance_product_line = fields.Boolean('Advance Product Line')


class HRExpenseExpense(models.Model):
    _inherit = "hr.expense.expense"
    _rec_name = "number"

    is_employee_advance = fields.Boolean(
        string='Employee Advance',
        readonly=False,
    )
    is_advance_clearing = fields.Boolean(
        string='Advance Clearing',
    )
    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Clear Advance',
    )
    advance_clearing_ids = fields.One2many(
        'hr.expense.expense',
        'advance_expense_id',
        string='Advance Clearing Expenses',
    )
    amount_to_clearing = fields.Float(
        string='Amount Balance',
        compute='_compute_amount_to_clearing',
        store=True,
        copy=False,
    )
    amount_approved = fields.Float(
        string='Approved Amount',
        readonly=False,
    )
    outstanding_advance_count = fields.Integer(
        string='Outstanding Advance Count',
        compute='_compute_outstanding_advance_count',
    )
    residual = fields.Float(
        string='Balance',
        digits=dp.get_precision('Account'),
        related='invoice_id.residual',
    )

    @api.model
    def _get_outstanding_advance_domain(self):
        domain = [('employee_id', '=', self.employee_id.id),
                  ('is_employee_advance', '=', True),
                  ('amount_to_clearing', '>', 0.0)]
        return domain

    @api.multi
    def _compute_outstanding_advance_count(self):
        for rec in self:
            domain = rec._get_outstanding_advance_domain()
            rec.outstanding_advance_count = self.search_count(domain)

    @api.multi
    def action_open_outstanding_advance(self):
        self.ensure_one()
        action = self.env.ref('hr_expense_advance_clearing.'
                              'action_expense_advance')
        result = action.read()[0]
        domain = self._get_outstanding_advance_domain()
        result.update({'domain': domain})
        return result

    @api.depends('advance_clearing_ids',
                 'advance_clearing_ids.state',
                 'advance_clearing_ids.amount',
                 'advance_clearing_ids.invoice_id.state',
                 'state')
    def _compute_amount_to_clearing(self):
        for expense in self:
            clearing_amount = 0.0
            if expense.state == 'paid':
                clearing_amount = expense.amount_approved
                if expense.advance_clearing_ids:
                    for clearing_advance in expense.advance_clearing_ids:
                        if clearing_advance.invoice_id.state in ('open',
                                                                 'paid'):
                            clearing_amount = clearing_amount - \
                                clearing_advance.amount + \
                                clearing_advance.invoice_id.amount_total - \
                                clearing_advance.residual
            expense.amount_to_clearing = clearing_amount

    @api.model
    def default_get(self, field_list):
        result = super(HRExpenseExpense, self).default_get(field_list)
        advance_product =\
            self.env.ref(
                'hr_expense_advance_clearing.product_product_employee_advance')
        if result.get('is_employee_advance', False):
            line = [(0, 0, {'product_id': advance_product.id,
                            'date_value': fields.Date.today(),
                            'name': advance_product.name,
                            'uom_id': advance_product.uom_id.id,
                            'unit_quantity': 1.0,
                            'is_advance_product_line': True, })]
            result.update({'line_ids': line})
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(HRExpenseExpense, self).\
            fields_view_get(view_id=view_id, view_type=view_type,
                            toolbar=toolbar, submenu=submenu)
        READONLY_FIELDS = ['product_id', 'uom_id', 'unit_quantity', 'tax_ids']
        LINE_VIEWS = ['tree', 'form']
        if self._context.get('is_employee_advance', False) and \
                view_type == 'form':
            for line_view in LINE_VIEWS:
                viewref = res['fields']['line_ids']['views'][line_view]
                doc = etree.XML(viewref['arch'])
                if line_view == 'tree':
                    nodes = doc.xpath("/tree")
                    for node in nodes:
                        node.set('create', 'false')
                for readonly_field in READONLY_FIELDS:
                    field_nodes =\
                        doc.xpath("//field[@name='%s']" % (readonly_field))
                    for field_node in field_nodes:
                        field_node.set('readonly', '1')
                        line_fields = viewref['fields']
                        setup_modifiers(field_node,
                                        line_fields[field_node.attrib['name']])
                viewref['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def expense_confirm(self):
        for expense in self:
            if not expense.is_advance_clearing and expense.amount <= 0.0:
                raise UserError(_('This expense have no lines,\
                or all lines with zero amount.'))
        return super(HRExpenseExpense, self).expense_confirm()

    @api.multi
    def _create_supplier_invoice_from_expense(self):
        invoice = super(HRExpenseExpense, self).\
            _create_supplier_invoice_from_expense()
        expense = self
        if expense.is_advance_clearing:
            advance_product = self.env.ref(
                'hr_expense_advance_clearing.product_product_employee_advance'
            )
            product_categ = advance_product.categ_id
            if (not advance_product.property_account_expense and
                    not product_categ.property_account_expense_categ):
                raise UserError(
                    _('Please define expense account '
                      'on Employee Advance Product.'))
            employee_advance = expense.amount
            if expense.amount > expense.advance_expense_id.amount_to_clearing:
                employee_advance = \
                    expense.advance_expense_id.amount_to_clearing
            invoice_line = expense.advance_expense_id.invoice_id.invoice_line
            if not invoice_line:
                raise UserError(_('No advance product line to reference'))
            advance_line = invoice_line[0]
            advance_line.copy({'invoice_id': invoice.id,
                               'price_unit': -employee_advance,
                               'sequence': 1, })
            invoice.write({'is_advance_clearing': True,
                           'invoice_type': 'advance_clearing_invoice'})
        elif expense.is_employee_advance:
            invoice.write({'invoice_type': 'expense_advance_invoice'})
        return invoice

    @api.model
    def create(self, vals):
        if vals.get('is_employee_advance', False) and \
                vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].get('hr.expense.advance')
        return super(HRExpenseExpense, self).create(vals)
