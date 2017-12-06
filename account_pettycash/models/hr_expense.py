# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HRExpense(models.Model):
    _inherit = "hr.expense.expense"

    pay_to = fields.Selection(
        selection_add=[('pettycash', 'Petty Cash')],
    )
    pettycash_id = fields.Many2one(
        'account.pettycash',
        string='Petty Cash',
        ondelete='restrict',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def _prepare_inv_header(self, partner_id, expense):
        if not partner_id:
            if expense.pay_to == 'pettycash':
                partner = expense.employee_id.user_id.partner_id
                if not partner:
                    raise ValidationError(
                        _('The employee must have a valid user in system'))
                if not partner.property_account_payable:
                    raise ValidationError(
                        _('The employee must have a payable account '
                          'set on referred user/partner.'))
                partner_id = partner.id

        res = super(HRExpense, self)._prepare_inv_header(partner_id,
                                                         expense)

        if expense.pay_to == 'pettycash':
            if not expense.pettycash_id:
                raise ValidationError(_('No Petty Cash selected!'))
            res['clear_pettycash_id'] = expense.pettycash_id.id
        return res

    @api.model
    def _prepare_pettycash_inv_lines(self, expense, pettycash):
        account = pettycash.account_id
        pettycash_line = {
            'sequence': 1,
            'name': account.name,
            'account_id': account.id,
            'price_unit': -expense.amount or 0.0,  # Negative
            'quantity': 1.0,
        }
        return pettycash_line

    @api.model
    def _create_negative_pettycash_line(self, expense, invoice):
        pettycash = expense.pettycash_id
        if not pettycash:
            raise ValidationError(
                _('Expense not specify petty cash to clear!'))
        pettycash_line = self._prepare_pettycash_inv_lines(expense, pettycash)
        invoice.write({'invoice_line': [(0, 0, pettycash_line)]})

    @api.multi
    def _create_supplier_invoice_from_expense(self):
        self.ensure_one()
        expense = self
        invoice = super(HRExpense, self).\
            _create_supplier_invoice_from_expense()
        if expense.pettycash_id:  # This expense will clear petty cash
            self._create_negative_pettycash_line(expense, invoice)
        return invoice
