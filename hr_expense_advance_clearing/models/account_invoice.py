# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # is_advance_clearing = fields.Boolean(
    #     string='Advance Clearing?',
    #     copy=False,
    # )
    supplier_invoice_type = fields.Selection(
        [('normal', 'Normal Invoice'),
         # Created from Normal Expense
         ('expense_expense_invoice', 'For Employee Expense'),
         # Created from Advance
         ('expense_advance_invoice', 'For Employee Advance'),
         # Created from Advance Clearing
         ('advance_clearing_invoice', 'For Advance Clearing'),
         ],
        string="Invoice Type",
        readonly=True,
        copy=False,
        default='normal',
    )
    advance_expense_id = fields.Many2one(
        'hr.expense.expense',
        string="Advance Expense",
        index=True,
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
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
        res['value'].update({'advance_expense_id': False})
        return res

    @api.onchange('advance_expense_id')
    def _onchange_advance_expense_id(self):
        # This method is called from Customer invoice to return money
        advance = self.advance_expense_id
        if advance:
            self.invoice_line = False
            advance_invoice = advance.invoice_id
            if advance_invoice.invoice_line:
                advance_line = advance_invoice.invoice_line[0]
                return_line = self.env['account.invoice.line'].new()
                # Prepare line
                _no_copy_fields = [
                    'id', 'expense_line_ids', '__last_update', 'price_unit',
                    'price_subtotal', 'discount',
                    'write_date', 'create_date', 'create_uid', 'write_uid',
                    'sequence', 'invoice_id', 'account_analytic_id',
                    'partner_id', 'purchase_line_id',
                ]
                _fields = [f for f, _x in return_line._fields.iteritems()]
                _copy_fields = list(set(_fields) - set(_no_copy_fields))
                for f in _copy_fields:
                    return_line[f] = advance_line[f]
                return_line['name'] = \
                    (u'รับคืนเงินยืมทดรองจ่ายของ AV เลขที่ %s' %
                     (advance.number,))
                self.invoice_line += return_line
            elif not advance_invoice:  # Case migration, no ref invoice
                if advance.line_ids:
                    advance_line = advance.line_ids[0]
                    advance_account_id = \
                        advance_line._get_non_product_account_id()
                    line_dict = advance_line.copy_data()
                    for line in line_dict:
                        # Remove some key
                        keys = ['expense_id', 'inrev_activity_id',
                                'description', 'ref']
                        for key in keys:
                            del line[key]
                        # Change some key
                        inv_exp = {'quantity': 'unit_quantity',
                                   'account_analytic_id': 'analytic_account',
                                   'price_unit': 'unit_amount',
                                   'invoice_line_tax_id': 'tax_ids', }
                        for new_key, old_key in inv_exp.iteritems():
                            line[new_key] = line.pop(old_key)
                        # Added fields
                        line['price_unit'] = False
                        line['account_id'] = advance_account_id
                        self.invoice_line += \
                            self.env['account.invoice.line'].new(line)

    # Not use ???
    # @api.model
    # def _get_invoice_total(self, invoice):
    #  amount_total = super(AccountInvoice, self)._get_invoice_total(invoice)
    #     return amount_total - self._prev_advance_amount(invoice)

    # Not use ???
    # @api.model
    # def _prev_advance_amount(self, invoice):
    #  advance_account = self.env.user.company_id.employee_advance_account_id
    #     if not advance_account:
    #         raise ValidationError(_('No Employee Advance Account has been '
    #                                 'set in Account Settings!'))
    #     lines = invoice.invoice_line
    #     # Advance with Negative Amount
    #     # kittiu: Performance Tuning
    #     # advance_lines = lines.filtered(lambda x: x.price_subtotal < 0 and
    #     #                                x.account_id == advance_account)
    #     # return sum([l.price_subtotal for l in advance_lines])
    #     amount = 0.0
    #     if lines:
    #         self._cr.execute("""
    #             select coalesce(sum(price_subtotal), 0.0) price_subtotal
    #             from account_invoice_line
    #             where id in %s
    #             and account_id = %s
    #             and price_subtotal < 0.0
    #         """, (tuple(lines.ids), advance_account.id))
    #         amount = self._cr.fetchone()[0]
    #     return amount

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            # Advance case, send back the final approved amount
            if invoice.supplier_invoice_type == 'expense_advance_invoice':
                invoice.expense_id.write({
                    'amount_advanced': invoice.amount_total})
            # Clearing case, do reconcile
            if invoice.supplier_invoice_type == 'advance_clearing_invoice'\
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
