# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_advance_clearing = fields.Boolean(
        string='Advance Clearing?',
    )
    invoice_type = fields.Selection(
        selection_add=[
            ('expense_advance_invoice', 'Employee Advance Invoice'),
            ('advance_clearing_invoice', 'Advance Clearing Invoice'),
        ],
    )
    ref_employee_id = fields.Many2one(
        'hr.employee',
        string='Related Employee ID',
        compute='_compute_ref_employee_id',
    )
    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string="Employee Advance Ref",
        help="Refer to Employee Advance this invoice is clearing/return",
    )

    @api.one
    @api.depends('partner_id')
    def _compute_ref_employee_id(self):
        self.ref_employee_id = (self.partner_id.user_ids and
                                self.partner_id.user_ids[0] and
                                self.partner_id.user_ids[0].employee_ids and
                                self.partner_id.user_ids[0].employee_ids[0] or
                                False)

    @api.onchange('advance_expense_id')
    def _onchange_advance_expense_id(self):
        # This method is called from Customer invoice to return money
        if self.advance_expense_id:
            self.invoice_line = []
            advance_invoice = self.advance_expense_id.invoice_id
            if advance_invoice.invoice_line:
                advance_line = advance_invoice.invoice_line[0]
                return_line = self.env['account.invoice.line'].new()
                # Prepare line
                return_line.product_id = advance_line.product_id
                return_line.name = advance_line.name
                return_line.quantity = 1.0
                self.invoice_line += return_line

    @api.model
    def _get_invoice_total(self, invoice):
        amount_total = super(AccountInvoice, self)._get_invoice_total(invoice)
        return amount_total - self._prev_advance_amount(invoice)

    @api.model
    def _prev_advance_amount(self, invoice):
        advance_product = self.env['ir.property'].get(
            'property_employee_advance_product_id', 'res.partner')
        if not advance_product:
            raise ValidationError(_('No Employee Advance Product has been '
                                    'set in HR Settings!'))
        lines = invoice.invoice_line
        # Advance with Negative Amount
        advance_lines = lines.filtered(lambda x: x.price_subtotal < 0 and
                                       x.product_id == advance_product)
        return sum([l.price_subtotal for l in advance_lines])

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            # Advance case, send back the final approved amount
            if invoice.invoice_type == 'expense_advance_invoice':
                invoice.expense_id.amount_advanced = invoice.amount_total
            # Clearing case, do reconcile
            if invoice.invoice_type == 'advance_clearing_invoice'\
                    and not invoice.amount_total:
                move_lines = \
                    self.env['account.move.line'].search(
                        [('state', '=', 'valid'),
                         ('account_id.type', '=', 'payable'),
                         ('reconcile_id', '=', False),
                         ('move_id', '=', invoice.move_id.id),
                         ('debit', '=', 0.0), ('credit', '=', 0.0)])
                move_lines.reconcile(type='manual')
        return result
