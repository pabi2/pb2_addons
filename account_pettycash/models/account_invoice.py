# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_pettycash = fields.Boolean(
        string='Petty Cash',
        default=False,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    clear_pettycash_id = fields.Many2one(
        'account.pettycash',
        string='Clear with Petty Cash',
        readonly=True,
        copy=False,
    )

    @api.multi
    @api.constrains('invoice_line')
    def _check_pettycash_amount(self):
        for rec in self:
            if not rec.is_pettycash:
                continue
            PettyCash = self.env['account.pettycash']
            pettycash = PettyCash.search(
                [('partner_id', '=', rec.partner_id.id)], limit=1)
            if not pettycash:
                raise ValidationError(_('%s is not a petty cash holder') %
                                      self.partner_id.name)
            balance = pettycash.pettycash_balance
            limit = pettycash.pettycash_limit
            max_amount = limit - balance
            account = pettycash.account_id
            # Looking for petty cash line
            inv_lines = rec.invoice_line.filtered(lambda l:
                                                  l.account_id == account)
            amount = sum([x.price_subtotal for x in inv_lines])
            company_currency = rec.company_id.currency_id
            amount_currency = rec.currency_id.compute(amount, company_currency)
            if float_compare(amount_currency, max_amount, 2) == 1:
                raise ValidationError(
                    _('Petty Cash balance is %s %s.\n'
                      'Max amount to add is %s %s.') %
                    ('{:,.2f}'.format(balance), company_currency.symbol,
                     '{:,.2f}'.format(max_amount), company_currency.symbol))

    @api.model
    def _prepare_pettycash_invoice_line(self, pettycash):
        inv_line = self.env['account.invoice.line'].new()
        inv_line.account_id = pettycash.account_id
        inv_line.name = pettycash.account_id.name
        inv_line.quantity = 1.0
        # Get suggested currency amount
        amount = pettycash.pettycash_limit - pettycash.pettycash_balance
        company_currency = self.env.user.company_id.currency_id
        amount_doc_currency = \
            company_currency.compute(amount, self.currency_id)
        inv_line.price_unit = amount_doc_currency
        return inv_line

    @api.onchange('is_pettycash')
    def _onchange_is_pettycash(self):
        self.invoice_line = False
        if self.is_pettycash:
            if not self.partner_id:
                self.is_pettycash = False
                raise ValidationError(_('Please select petty cash holder'))
            PettyCash = self.env['account.pettycash']
            # Selected parenter must be petty cash holder
            pettycash = PettyCash.search(
                [('partner_id', '=', self.partner_id.id)], limit=1)
            if not pettycash:
                self.is_pettycash = False
                raise ValidationError(_('%s is not a petty cash holder') %
                                      self.partner_id.name)
            inv_line = self._prepare_pettycash_invoice_line(pettycash)
            self.invoice_line += inv_line

    @api.multi
    def invoice_validate(self):
        result = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            # Petty cash case, do reconcile
            if invoice.clear_pettycash_id:
                balance = invoice.clear_pettycash_id.pettycash_balance
                if invoice.amount_total:
                    raise ValidationError(
                        _('Please clear petty cash with full amount!\n'
                          'Final total amount should be 0.0.'))
                # Set partner to petty cash line
                account = invoice.clear_pettycash_id.account_id
                partner = invoice.clear_pettycash_id.partner_id
                move_lines = invoice.move_id.line_id
                move_lines = move_lines.filtered(lambda l:
                                                 l.account_id == account)
                move_lines.write({'partner_id': partner.id})
                # Reconcile it.
                move_lines = \
                    self.env['account.move.line'].search(
                        [('state', '=', 'valid'),
                         ('account_id.type', '=', 'payable'),
                         ('reconcile_id', '=', False),
                         ('move_id', '=', invoice.move_id.id),
                         ('debit', '=', 0.0), ('credit', '=', 0.0)])
                move_lines.reconcile(type='manual')
                # Clear cache first.
                invoice.invalidate_cache()
                if invoice.clear_pettycash_id.pettycash_balance < 0.0:
                    raise ValidationError(
                        _('Requested amount exceed current '
                          'petty cash balance: %s') %
                        '{:,.2f}'.format(balance))
        return result
