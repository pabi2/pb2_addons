# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_advance_clearing = fields.Boolean(
        string='Advance Clearing?',
        copy=False,
    )
    invoice_type = fields.Selection(
        selection_add=[
            ('expense_advance_invoice', 'Employee Advance Invoice'),
            ('advance_clearing_invoice', 'Advance Clearing Invoice'),
        ],
    )
    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string="Advance Expense",
        copy=False,
        help="Refer to Employee Advance this invoice is clearing/return",
    )

    @api.multi
    def onchange_partner_id(self, ttype, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            ttype, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if not res:
            res = {}
        if 'value' not in res:
            res['value'] = {}
        if 'domain' not in res:
            res['domain'] = {}

        res['value'].update({'advance_expense_id': False})
        if not partner_id:
            domain = [('id', 'in', [])]
            res['domain'].update({'advance_expense_id': domain})
        else:
            partner = self.env['res.partner'].browse(partner_id)
            ref_employee_id = (partner.user_ids and
                               partner.user_ids[0] and
                               partner.user_ids[0].employee_ids and
                               partner.user_ids[0].employee_ids[0].id or
                               False)
            domain = [('is_employee_advance', '=', True),
                      ('state', 'in', ('open', 'paid')),
                      ('employee_id', '=', ref_employee_id),
                      ('amount_to_clearing', '>', 0.0)]
            res['domain'].update({'advance_expense_id': domain})
        return res

    @api.onchange('advance_expense_id')
    def _onchange_advance_expense_id(self):
        # This method is called from Customer invoice to return money
        if self.advance_expense_id:
            self.invoice_line = []
            advance_invoice = self.advance_expense_id.invoice_id
            if advance_invoice.invoice_line:
                Expense = self.env['hr.expense.expense']
                advance_line = advance_invoice.invoice_line[0]
                return_line = self.env['account.invoice.line'].new()
                # Prepare line
                return_line.product_id = advance_line.product_id
                return_line.account_id = Expense.\
                    _choose_account_from_exp_line(advance_line,
                                                  self.fiscal_position)
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
