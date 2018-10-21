# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare


class AccuontBankReceiptMultipleReconcile(models.Model):
    _name = 'account.bank.receipt.multiple.reconcile'
    _description = 'Account Bank Receipt Multiple Reconcile'

    account_id = fields.Many2one(
        'account.account',
        string='Reconcile Account',
        domain=[('type', 'not in', ['view', 'closed']),
                ('reconcile', '!=', True)],
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
        size=500,
    )
    bank_receipt_id = fields.Many2one(
        'account.bank.receipt',
        string='Related Bank Receipt',
        index=True,
        ondelete='cascade',
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
        string="Writeoff Amount",
        readonly=True,
        compute="_compute_writeoff_amount",
        help="Computed as the difference between the amount\
        stated in the voucher and the sum of allocation\
        on the voucher lines.",
    )
    payment_difference_amount = fields.Float(
        string="Difference Amount",
        readonly=True,
        compute="_compute_writeoff_amount",
        help="Computed as the difference between the amount\
        stated in the voucher and the sum of allocation\
        on the voucher lines.",
    )
    total_amount = fields.Float(
        string="Computed Total Amount",
        copy=False,
    )
    manual_total_amount = fields.Float(
        string="Total Amount",
        readonly=True,
        default=0.0,
        states={'draft': [('readonly', False)]},
        required=True,
    )

    @api.multi
    def validate_bank_receipt(self):
        for receipt in self:
            if float_compare(receipt.writeoff_amount, 0.0, 2) != 0:
                raise ValidationError(
                    _('Writeoff Amount must be 0.0 to validate!'))
        res = super(AccountBankReceipt, self).validate_bank_receipt()
        return res

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
        'multiple_reconcile_ids',
        'multiple_reconcile_ids.amount'
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
            writeoffline_amount = 0.0
            if receipt.multiple_reconcile_ids:
                writeoffline_amount =\
                    sum([l.amount for l in receipt.multiple_reconcile_ids])
            receipt.payment_difference_amount = receipt.total_amount - total
            receipt.writeoff_amount = (receipt.total_amount -
                                       writeoffline_amount -
                                       total)

    @api.model
    def _create_writeoff_move_line_hook(self, move):
        super(AccountBankReceipt, self)._create_writeoff_move_line_hook(move)
        if self.payment_difference_amount != 0.0:
            MoveLine = self.env['account.move.line']
            if self.payment_difference_amount != 0.0 and \
                    self.multiple_reconcile_ids:
                for writeofline in self.multiple_reconcile_ids:
                    move_line_val = \
                        self._prepare_writeoff_move_line(writeofline)
                    move_line_val['move_id'] = move.id
                    MoveLine.create(move_line_val)
        return True

    @api.model
    def _do_reconcile(self, to_reconcile_lines):
        if self.payment_difference_amount != 0.0 and \
                self.multiple_reconcile_ids:
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
    def _prepare_counterpart_move_lines_vals(
            self, receipt, total_debit, total_amount_currency):
        vals = super(AccountBankReceipt, self).\
            _prepare_counterpart_move_lines_vals(receipt, total_debit,
                                                 total_amount_currency)
        if self.payment_difference_amount != 0.0 and \
                self.multiple_reconcile_ids:
            vals['debit'] = self.total_amount
        return vals

    @api.model
    def _prepare_writeoff_move_line(self, writeofline):
        credit = 0.0
        debit = 0.0
        if writeofline.amount > 0.0:
            credit = abs(writeofline.amount)
        else:
            debit = abs(writeofline.amount)
        return {
            'name': writeofline.note,
            'credit': credit,
            'debit': debit,
            'account_id': writeofline.account_id.id,
            'partner_id': False,
            'currency_id': False,
            'amount_currency': False,
            'analytic_account_id': writeofline.analytic_id and
            writeofline.analytic_id.id or False,
        }
