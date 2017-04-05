# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError


class AccuontBankReceiptMultipleReconcile(models.Model):
    _name = 'account.bank.receipt.multiple.reconcile'
    _description = 'Account Bank Receipt Multiple Reconcile'

    account_id = fields.Many2one(
        'account.account',
        string='Reconcile Account',
        required=True,
    )
    amount = fields.Float(
        string='Amount',
        digits_compute=dp.get_precision('Account'),
        required=True,
    )
    note = fields.Char(
        string='Comment',
        required=True,
    )
    bank_receipt_id = fields.Many2one(
        'account.bank.receipt',
        string='Related Bank Receipt',
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )


class AccountBankReceipt(models.Model):
    _inherit = 'account.bank.receipt'

    multiple_reconcile_ids = fields.One2many(
        'account.bank.receipt.multiple.reconcile',
        'bank_receipt_id',
        string='Reconcile Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    writeoff_amount = fields.Float(
        string="Difference Amount",
        readonly=True,
        compute="_compute_writeoff_amount",
        help="Computed as the difference between the amount\
        stated in the voucher and the sum of allocation\
        on the voucher lines.",
    )
    payment_option = fields.Selection(
        selection=[
            ('without_writeoff', 'Keep Open'),
            ('with_writeoff', 'Reconcile Payment Balance')
        ],
        string='Payment Difference',
        readonly=True,
        default="without_writeoff",
        help="This field helps you to choose what you want\
        to do with the eventual difference between the paid \
        amount and the sum of allocated amounts.\
        You can either choose to keep open this difference\
        on the partner's account, or reconcile it with the payment(s)",
    )
    total_amount = fields.Float(
        string="Computed Total Amount",
        copy=False,
    )
    manual_total_amount = fields.Float(
        string="Total Amount",
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True,
    )

    @api.multi
    @api.depends('manual_total_amount')
    def _compute_bank_receipt(self):
        res = super(AccountBankReceipt, self)._compute_bank_receipt()
        for receipt in self:
            receipt.total_amount = receipt.manual_total_amount
        return res

    @api.multi
    @api.depends(
        'total_amount',
    )
    def _compute_writeoff_amount(self):
        for receipt in self:
            total = 0.0
            currency_none_same_company_id = False
            if receipt.company_id.currency_id != receipt.currency_id:
                currency_none_same_company_id = receipt.currency_id.id
            for line in receipt.bank_intransit_ids:
                if currency_none_same_company_id:
                    total += line.amount_currency
                else:
                    total += line.debit
            receipt.writeoff_amount = total - receipt.total_amount

    @api.model
    def _create_writeoff_move_line(self, move):
        writeoflines = super(AccountBankReceipt,
                             self)._create_writeoff_move_line(move)
        if self.writeoff_amount != 0.0 and self.multiple_reconcile_ids:
            if len(self.bank_intransit_ids) > 1\
                    and self.writeoff_amount != 0.0:
                raise UserError(
                    _('You can use write-off only for\
                        single bank intransit line!'))
            aml_obj = self.env['account.move.line']
            for writeofline in self.multiple_reconcile_ids:
                move_line_val = self._prepare_writeoff_move_line(writeofline)
                move_line_val['move_id'] = move.id
                writeoflines += aml_obj.create(move_line_val)
        return writeoflines

    @api.model
    def _do_reconcile(self, to_reconcile_lines):
        if self.writeoff_amount != 0.0 and self.multiple_reconcile_ids:
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile_partial(type='manual')
            return True
        else:
            return super(AccountBankReceipt,
                         self)._do_reconcile(to_reconcile_lines)

    @api.onchange('writeoff_amount')
    def onchange_writeoff_amount(self):
        for receipt in self:
            if receipt.writeoff_amount == 0.0:
                receipt.multiple_reconcile_ids = [(6, 0, [])]

    @api.model
    def _prepare_move_line_vals(self, line):
        vals = super(AccountBankReceipt, self)._prepare_move_line_vals(line)
        if self.writeoff_amount != 0.0 and self.multiple_reconcile_ids:
            vals['credit'] = self.total_amount
        return vals

    @api.model
    def _prepare_writeoff_move_line(self, writeofline):
        credit = 0.0
        debit = 0.0
        if self.writeoff_amount > 0.0:
            credit = writeofline.amount
        else:
            debit = writeofline.amount
        return {
            'name': writeofline.note,
            'credit': credit,
            'debit': debit,
            'account_id': writeofline.account_id.id,
            'partner_id': self.company_partner_id.id,
            'currency_id': False,
            'amount_currency': 0 * -1,
        }
