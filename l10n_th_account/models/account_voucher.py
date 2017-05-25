# -*- coding: utf-8 -*-
import time
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
from openerp.addons.l10n_th_account.models.res_partner \
    import INCOME_TAX_FORM

WHT_CERT_INCOME_TYPE = [('1', '1.เงินเดือน ค่าจ้าง ฯลฯ 40(1)'),
                        ('2', '2.ค่าธรรมเนียม ค่านายหน้า ฯลฯ 40(2)'),
                        ('3', '3.ค่าแห่งลิขสิทธิ์ ฯลฯ 40(3)'),
                        ('5', '5.ค่าจ้างทำของ ค่าบริการ ฯลฯ 3 เตรส'),
                        ('6', '6.อื่นๆ')]

TAX_PAYER = [('withholding', 'Withholding'),
             ('paid_one_time', 'Paid One Time')]


class common_voucher(object):

    @api.model
    def _to_invoice_currency(self, invoice, journal, amount):
        currency = invoice.currency_id.with_context(
            date=invoice.date_invoice or
            datetime.today())
        company_currency = (journal.currency and
                            journal.currency.id or
                            journal.company_id.currency_id)
        amount = currency.compute(float(amount), company_currency, round=False)
        return amount

    @api.model
    def _to_voucher_currency(self, invoice, journal, amount):
        currency = invoice.currency_id.with_context(
            date=invoice.date_invoice or
            datetime.today())
        company_currency = (journal.currency and
                            journal.currency.id or
                            journal.company_id.currency_id)
        amount = currency.compute(float(amount), company_currency, round=False)
        return amount


class AccountVoucher(common_voucher, models.Model):
    _inherit = 'account.voucher'

    @api.multi
    @api.depends('amount', 'line_cr_ids', 'line_dr_ids')
    def _get_writeoff_amount(self):
        """ Overwrite """
        for voucher in self:
            voucher.writeoff_amount = self._calc_writeoff_amount(voucher)

    # Columns
    tax_line = fields.One2many(
        'account.voucher.tax',
        'voucher_id',
        string='Tax Lines',
        readonly=False,
    )
    tax_line_normal = fields.One2many(
        'account.voucher.tax',
        'voucher_id',
        string='Tax Lines (Normal)',
        readonly=True, states={'draft': [('readonly', False)]},
        domain=[('tax_code_type', '=', 'normal')],
    )
    tax_line_undue = fields.One2many(
        'account.voucher.tax',
        'voucher_id',
        string='Tax Lines (Undue)',
        readonly=True, states={'draft': [('readonly', False)]},
        domain=[('tax_code_type', '=', 'undue')],
    )
    tax_line_wht = fields.One2many(
        'account.voucher.tax',
        'voucher_id',
        string='Tax Lines (Withholding)',
        readonly=True, states={'draft': [('readonly', False)]},
        domain=[('tax_code_type', '=', 'wht')],
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        readonly=True,
        help="Specify form for withholding tax, default with setup in supplier"
    )
    wht_sequence = fields.Integer(
        string='WHT Sequence',
        readonly=True,
        help="Running sequence for the same period. Reset every period",
    )
    wht_sequence_display = fields.Char(
        string='WHT Sequence',
        compute='_compute_wht_sequence_display',
        store=True,
    )
    wht_period_id = fields.Many2one(
        'account.period',
        string='WHT Period',
        readonly=True,
    )
    tax_payer = fields.Selection(
        TAX_PAYER,
        string='Tax Payer',
        readonly=True, states={'draft': [('readonly', False)]},
    )
    recognize_vat_move_id = fields.Many2one(
        'account.move',
        string='Recognize VAT Entry',
        ondelete='set null',
        readonly=True,
    )
    auto_recognize_vat = fields.Boolean(
        related='company_id.auto_recognize_vat',
        string='Auto recognize undue VAT',
        readonly=True,
    )
    writeoff_amount = fields.Float(
        compute=_get_writeoff_amount,
        string='Difference Amount',
        readonly=True,
        help="Computed as the difference between the amount stated in the "
        "voucher and the sum of allocation on the voucher lines.",
    )
    _sql_constraints = [
        ('wht_seq_uunique',
         'unique (wht_period_id, wht_sequence, income_tax_form)',
         'WHT Sequence must be unique!'),
    ]

    @api.model
    def _calc_writeoff_amount(self, voucher):
        debit, credit = 0.0, 0.0
        sign = voucher.type == 'payment' and -1 or 1
        for l in voucher.line_dr_ids:
            debit += l.amount + \
                l.amount_wht + l.amount_retention  # Fixed here
        for l in voucher.line_cr_ids:
            credit += l.amount + \
                l.amount_wht + l.amount_retention  # Fixed here
        currency = voucher.currency_id or voucher.company_id.currency_id
        return currency.round(voucher.amount - sign * (credit - debit))

    @api.multi
    @api.depends('wht_sequence')
    def _compute_wht_sequence_display(self):
        for rec in self:
            if rec.wht_period_id and rec.wht_sequence:
                date_start = rec.wht_period_id.date_start
                mo = datetime.strptime(date_start,
                                       '%Y-%m-%d').date().month
                month = '{:02d}'.format(mo)
                sequence = '{:04d}'.format(rec.wht_sequence)
                rec.wht_sequence_display = '%s/%s' % (month, sequence)

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            if voucher.type == 'payment' and not voucher.auto_recognize_vat:
                if voucher.recognize_vat_move_id:
                    raise ValidationError(
                        _('To Unreconcile this payment, you must reverse '
                          'the Recognized VAT Entry first.'))
        super(AccountVoucher, self).cancel_voucher()

    @api.model
    def _compute_writeoff_amount(self,
                                 line_dr_ids,
                                 line_cr_ids,
                                 amount, _type):
        res = super(AccountVoucher, self)._compute_writeoff_amount(
            line_dr_ids,
            line_cr_ids,
            amount, _type)
        debit = credit = 0.0
        sign = _type == 'payment' and -1 or 1
        for l in line_dr_ids:
            if isinstance(l, dict):
                debit += l.get('amount_wht', 0.0) + \
                    l.get('amount_retention', 0.0)  # Added
        for l in line_cr_ids:
            if isinstance(l, dict):
                credit += l.get('amount_wht', 0.0) + \
                    l.get('amount_retention', 0.0)  # Added
        return res - sign * (credit - debit)

    # Note: This method is not exactly the same as the line's one.
    @api.model
    def _get_amount_wht_ex(self, partner_id, move_line_id, amount_original,
                           original_wht_amt, original_retention_amt, amount):
        tax_obj = self.env['account.tax']
        partner_obj = self.env['res.partner']
        move_line_obj = self.env['account.move.line']
        partner = partner_obj.browse(partner_id)
        move_line = move_line_obj.browse(move_line_id)
        amount_wht = 0.0
        if move_line.invoice:
            invoice = move_line.invoice
            for line in invoice.invoice_line:
                revised_price = line.price_unit * \
                    (1 - (line.discount or 0.0) / 100.0)
                # Only WHT
                is_wht = True in [x.is_wht
                                  for x in
                                  line.invoice_line_tax_id] or False
                if is_wht:
                    new_amt_orig = (amount_original -
                                    original_wht_amt -
                                    original_retention_amt)
                    ratio = (new_amt_orig and amount / new_amt_orig or 0.0)
                    taxes_list = line.invoice_line_tax_id.compute_all(
                        revised_price * ratio,
                        line.quantity,
                        line.product_id,
                        partner)['taxes']
                    for tax in taxes_list:
                        account_tax = tax_obj.browse(tax['id'])
                        if account_tax.is_wht:
                            # Check Threshold
                            base = revised_price * line.quantity
                            t = account_tax.read(['threshold_wht'])
                            if abs(base) and abs(base) < t[0]['threshold_wht']:
                                continue
                            amount_wht += tax['amount']
            # Convert to voucher currency
            amount_wht = self._to_voucher_currency(invoice,
                                                   move_line.journal_id,
                                                   amount_wht)
        return float(amount), float(amount_wht)

    # Note: This method is not exactly the same as the line's one.
    @api.model
    def _get_amount_retention_ex(self, partner_id, move_line_id,
                                 amount_original, original_retention_amt,
                                 original_wht_amt, amount):
        move_line_obj = self.env['account.move.line']
        move_line = move_line_obj.browse(move_line_id)
        amount_retention = 0.0
        if move_line.invoice:
            invoice = move_line.invoice
            if invoice.retention_on_payment:
                # Here is what different from _get_amount_retention()
                new_amt_orig = (amount_original -
                                original_retention_amt -
                                original_wht_amt)
                ratio = (new_amt_orig and amount / new_amt_orig or 0.0)
                amount_retention = invoice.amount_retention * ratio
                # Change to currency at invoicing time.
                amount_retention = self._to_voucher_currency(
                    invoice,
                    move_line.journal_id,
                    amount_retention)
        return float(amount), float(amount_retention)

    # The original recompute_voucher_lines() do not aware of withholding.
    # Here we will re-adjust it. As such, the amount allocation will be reduced
    # and carry to the next lines.
    @api.multi
    def recompute_voucher_lines(self, partner_id, journal_id,
                                price, currency_id, ttype, date):
        res = super(AccountVoucher, self).recompute_voucher_lines(
            partner_id, journal_id,
            price, currency_id, ttype, date)
        line_cr_ids = res['value']['line_cr_ids']
        line_dr_ids = res['value']['line_dr_ids']
        # For Register Payment on Invoice, remove
        sign = 0
        move_line_obj = self.env['account.move.line']
        remain_amount = float(price)
        if ttype == 'payment':
            lines = line_cr_ids + line_dr_ids
        else:
            lines = line_dr_ids + line_cr_ids
        active_cr_lines, active_dr_lines = [], []
        for line in lines:
            if not isinstance(line, dict):
                continue
            amount, amount_wht, amount_retention = 0.0, 0.0, 0.0
            move_line = move_line_obj.browse(line['move_line_id'])
            invoice_id = self._context.get('invoice_id', False)
            if invoice_id and move_line.invoice.id != invoice_id:
                continue
            # Test to get full wht, retention first
            line_obj = self.env['account.voucher.line']
            original_amount, \
                original_wht_amt = line_obj._get_amount_wht(
                    partner_id,
                    line['move_line_id'],
                    line['amount_original'],
                    line['amount_original'])
            original_amount, \
                original_retention_amt = line_obj._get_amount_retention(
                    partner_id,
                    line['move_line_id'],
                    line['amount_original'],
                    line['amount_original'])
            # Full amount to reconcile
            new_amt_orig = (original_amount -
                            original_wht_amt -
                            original_retention_amt)
            ratio = original_amount > 0.0 and \
                new_amt_orig / original_amount or 0.0
            amount_alloc = line['amount_unreconciled'] * ratio
            # Allocations Amount
            if ttype == 'payment':  # Supplier Payment
                if line['type'] == 'cr':  # always full allocation.
                    sign = 1
                    amount_alloc = amount_alloc
                else:  # cr, spend the remaining
                    sign = -1
                    if remain_amount == 0.0:
                        amount_alloc = 0.0
                    else:
                        if 'default_amount' in self._context:  # Case Dialog
                            amount_alloc = amount_alloc
                        else:
                            amount_alloc = amount_alloc > remain_amount and \
                                remain_amount or amount_alloc
            else:  # Customer Payment
                if line['type'] == 'dr':  # always full allocation.
                    sign = 1
                    amount_alloc = amount_alloc
                else:  # cr, spend the remaining
                    sign = -1
                    if remain_amount == 0.0:
                        amount_alloc = 0.0
                    else:
                        if 'default_amount' in self._context:  # Case Dialog
                            amount_alloc = amount_alloc
                        else:
                            amount_alloc = amount_alloc > remain_amount and \
                                remain_amount or amount_alloc
            # ** Calculate withholding amount **
            if amount_alloc:
                amount, amount_wht = self._get_amount_wht_ex(
                    partner_id,
                    line['move_line_id'],
                    line['amount_original'],
                    original_wht_amt,
                    original_retention_amt,
                    amount_alloc)
                amount, amount_retention = self._get_amount_retention_ex(
                    partner_id,
                    line['move_line_id'],
                    line['amount_original'],
                    original_retention_amt,
                    original_wht_amt,
                    amount_alloc)
            # Adjust remaining
            remain_amount = remain_amount + (sign * amount_alloc)
            line['amount'] = amount + amount_wht + amount_retention
            line['amount_wht'] = -amount_wht
            line['amount_retention'] = -amount_retention
            line['reconcile'] = line['amount'] == line['amount_unreconciled']
            if line['type'] == 'cr':
                active_cr_lines.append(line)
            if line['type'] == 'dr':
                active_dr_lines.append(line)
        # For case Register Payment form invoice, remove zero amount lines
        if 'default_amount' in self._context:
            res['value']['line_cr_ids'] = active_cr_lines
            res['value']['line_dr_ids'] = active_dr_lines
        return res

    @api.multi
    def button_reset_taxes(self):
        if self._context.get('no_reset_tax', False):
            return True
        for voucher in self:
            if voucher.state == 'posted':
                continue
            self._cr.execute("""
                DELETE FROM account_voucher_tax
                WHERE voucher_id=%s AND manual is False
                """, (voucher.id,))
            partner = voucher.partner_id
            if partner.lang:
                voucher.with_context(lang=partner.lang)
            voucher_tax_obj = self.env['account.voucher.tax']
            for tax in voucher_tax_obj.compute(voucher).values():
                voucher_tax_obj.create(tax)
        return True

    @api.multi
    def write(self, vals):
        """ automatic compute tax then save """
        res = super(AccountVoucher, self).write(vals)
        # When editing only tax amount, do not reset tax
        to_update = True
        if vals.get('tax_line_normal', False):
            for tax_line in vals.get('tax_line_normal'):
                if tax_line[0] == 1 and 'amount' in tax_line[2]:  # 1 = update
                    to_update = False
        if to_update:
            self.button_reset_taxes()
        return res

    @api.model
    def _finalize_line_total(self, voucher, line_total,
                             move_id, company_currency,
                             current_currency):
        line_total = super(AccountVoucher, self)._finalize_line_total(
            voucher, line_total, move_id, company_currency, current_currency)
        net_tax = 0.0
        net_retention = 0.0
        if voucher.type in ('receipt', 'payment'):
            net_tax = self.voucher_move_line_tax_create(
                voucher, move_id, company_currency, current_currency)
            if not self._context.get('recognize_vat', False):
                net_retention = self.voucher_move_line_retention_create(
                    voucher, move_id, company_currency, current_currency)
        line_total = line_total + net_tax + net_retention
        return line_total

    @api.model
    def voucher_move_line_tax_create(self, voucher, move_id,
                                     company_currency, current_currency):
        """ New Method for account.voucher.tax """
        move_obj = self.env['account.move']
        avt_obj = self.env['account.voucher.tax']
        # one move line per tax line
        vtml = avt_obj.move_line_get(voucher)
        # create gain/loss from currency between invoice and voucher
        vtml = self.compute_tax_currency_gain(voucher, vtml)
        # create one move line for the total and adjust the other lines amount
        net_tax_currency, vtml = self.compute_net_tax(voucher,
                                                      company_currency,
                                                      vtml)
        # Create move line,
        lines = [(0, 0, ml) for ml in vtml]
        move = move_obj.browse(move_id)
        move.write({'line_id': lines})
#         for ml in vtml:
#             ml.update({'move_id': move_id})
#             move_line_obj.create(ml)
        return net_tax_currency

    @api.model
    def voucher_move_line_retention_create(self, voucher, move_id,
                                           company_currency, current_currency):
        """ New Method for Retention """
        move_obj = self.env['account.move']
        # one move line per retention line
        vtml = self.move_line_get(voucher)
        # create gain/loss from currency between invoice and voucher
        net_retention_currency, vtml = self.compute_net_retention(
            voucher, company_currency, vtml)
        # Create move line,
        lines = [(0, 0, ml) for ml in vtml]
        move = move_obj.browse(move_id)
        move.write({'line_id': lines})
#         for ml in vtml:
#             ml.update({'move_id': move_id})
#             move_line_obj.create(ml)
        return net_retention_currency

    @api.model
    def move_line_get(self, voucher):
        res = []
        self._cr.execute("""
            SELECT * FROM account_voucher_line
            WHERE voucher_id=%s and amount_retention != 0
        """, (voucher.id,))
        for t in self._cr.dictfetchall():
            account_id = False
            company = self.env.user.company_id
            if voucher.type in ('sale', 'receipt'):
                account_id = company.account_retention_customer.id
            else:
                account_id = company.account_retention_supplier.id
            res.append({
                'type': 'src',
                'name': _('Retention Amount'),
                'price_unit': t['amount_retention'],
                'quantity': 1,
                'price': t['amount_retention'],
                'account_id': account_id,
                'product_id': False,
                'uos_id': False,
                'account_analytic_id': False,
                'taxes': False,
            })
        return res

    @api.model
    def compute_net_tax(self, voucher,
                        company_currency,
                        voucher_tax_move_lines):
        """ New Method to compute the net tax (cr/dr) """
        total = 0
        total_currency = 0
        cur_obj = self.env['res.currency']
        current_currency = self._get_current_currency(voucher.id)
        for i in voucher_tax_move_lines:
            if current_currency != company_currency:
                date = voucher.date or time.strftime('%Y-%m-%d')
                cur_obj.with_context(date=date)
                i['currency_id'] = current_currency
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(current_currency,
                                             company_currency,
                                             i['price'])
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            debit = credit = 0.0
            if voucher.type == 'payment':
                debit = i['amount_currency'] or i['price']
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
            else:
                credit = i['amount_currency'] or i['price']
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
                i['price'] = - i['price']
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            i['period_id'] = voucher.period_id.id
            i['partner_id'] = voucher.partner_id.id
            i['date'] = voucher.date
            i['date_maturity'] = voucher.date_due
            i['debit'] = debit
            i['credit'] = credit
        return total_currency, voucher_tax_move_lines

    @api.model
    def compute_net_retention(self, voucher,
                              company_currency,
                              voucher_retention_move_lines):
        """ New Method to compute the net tax (cr/dr) """
        total = 0
        total_currency = 0
        cur_obj = self.env['res.currency']
        current_currency = self._get_current_currency(voucher.id)
        for i in voucher_retention_move_lines:
            if current_currency != company_currency:
                date = voucher.date or time.strftime('%Y-%m-%d')
                cur_obj.with_context(date=date)
                i['currency_id'] = current_currency
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(current_currency,
                                             company_currency,
                                             i['price'])
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            debit = credit = 0.0
            if voucher.type == 'payment':
                debit = i['amount_currency'] or i['price']
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
            else:
                credit = i['amount_currency'] or i['price']
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
                i['price'] = - i['price']
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            i['period_id'] = voucher.period_id.id
            i['partner_id'] = voucher.partner_id.id
            i['date'] = voucher.date
            i['date_maturity'] = voucher.date_due
            i['debit'] = debit
            i['credit'] = credit
        return total_currency, voucher_retention_move_lines

    @api.model
    def compute_tax_currency_gain(self, voucher, voucher_tax_move_lines):
        """ New Method to add gain loss from currency for tax """
        for i in voucher_tax_move_lines:
            if 'tax_currency_gain' in i and i['tax_currency_gain']:
                debit = credit = 0.0
                if voucher.type == 'payment':
                    debit = i['tax_currency_gain']
                else:
                    credit = i['tax_currency_gain']
                if debit < 0:
                    credit = -debit
                    debit = 0.0
                if credit < 0:
                    debit = -credit
                    credit = 0.0
                gain_account_id, loss_account_id = False, False
                company = voucher.company_id
                income_acct = company.income_currency_exchange_account_id
                expense_acct = company.expense_currency_exchange_account_id
                if income_acct and expense_acct:
                    gain_account_id = income_acct.id
                    loss_account_id = expense_acct.id
                else:
                    raise ValidationError(
                        _('No gain/loss accounting defined in the system!'))
                if debit > 0.0 or credit > 0.0:
                    sign = debit - credit < 0 and -1 or 1
                    voucher_tax_move_lines.append({
                        'type': 'tax',
                        'name': _('Gain/Loss Exchange Rate'),
                        'quantity': 1,
                        'price': sign * (credit or -debit),
                        'account_id': (credit and
                                       gain_account_id or
                                       loss_account_id)
                    })
        return voucher_tax_move_lines

    @api.multi
    def onchange_journal(self, journal_id, line_ids, tax_id, partner_id,
                         date, amount, ttype, company_id):
        res = super(AccountVoucher, self).onchange_journal(
            journal_id, line_ids, tax_id, partner_id,
            date, amount, ttype, company_id)
        if 'default_amount' in self._context and res:
            vline_obj = self.env['account.voucher.line']
            if amount == 0.0:  # Sum amount for the line to reconcile
                lines = ['line_cr_ids', 'line_dr_ids']
                for line in lines:
                    for l in res['value'].get(line, []):
                        val = vline_obj.onchange_reconcile(
                            partner_id,
                            l['move_line_id'], l['amount_original'],
                            True, l['amount'], l['amount_unreconciled'])
                        amount += (val['value']['amount'] +
                                   val['value']['amount_wht'] +
                                   val['value']['amount_retention'])
                # Reverse sign for refund
                if self._context.get('invoice_type') in \
                        ('out_refund', 'in_refund'):
                    amount = -amount
                res['value'].update({'amount': amount})
        return res

    @api.multi
    def action_move_line_create(self):
        """ This is the cut down version of action_move_line_create()
            It just post the clearing between due and undue """
        if not self.env.user.company_id.auto_recognize_vat and \
                self._context.get('recognize_vat', False):
            # Start its own
            context = self._context.copy()
            move_pool = self.env['account.move']
            for voucher in self:
                if voucher.recognize_vat_move_id:
                    raise ValidationError(_('Recognize VAT Entry already exists'))
                company_currency = self._get_company_currency(voucher.id)
                current_currency = self._get_current_currency(voucher.id)
                context = self.with_context(context)._sel_context(voucher.id)
                move_dict = \
                    self.with_context(context).account_move_get(voucher.id)
                journal = self.env.user.company_id.recognize_vat_journal_id
                today = fields.Date.context_today(self)
                period_id = self.env['account.period'].find(self.date)[:1]
                move_dict.update({
                    'name': '/',
                    'journal_id': journal.id,
                    'date': today,
                    'period_id': period_id.id,
                })
                move = move_pool.with_context(context).\
                    create(move_dict)
                self.with_context(context).\
                    _finalize_line_total(voucher, 0.0, move.id,
                                         company_currency, current_currency)
                voucher.write({
                    'recognize_vat_move_id': move.id,
                })
            # Call just to by pass in hook, but still benefit from others
            super(AccountVoucher,
                  self.with_context(bypass=True)).action_move_line_create()
        else:
            super(AccountVoucher, self).action_move_line_create()
        return True

    @api.multi
    def _assign_wht_sequence(self):
        """ Only if not assigned, this method will assign next sequence """
        Period = self.env['account.period']
        for voucher in self:
            if not voucher.income_tax_form:
                raise ValidationError(_("No Income Tax Form selected, "
                                        "can not assign WHT Sequence"))
            if voucher.wht_sequence:
                continue
            wht_period = Period.find(voucher.date_value)[:1]
            wht_sequence = \
                voucher._get_next_wht_sequence(voucher.income_tax_form,
                                               wht_period)
            voucher.write({'wht_period_id': wht_period.id,
                           'wht_sequence': wht_sequence})

    # @api.model
    # def _get_next_wht_sequence(self, income_tax_form, wht_period_id):
    #     self._cr.execute("""
    #         select coalesce(max(wht_sequence), 0) + 1
    #         from account_voucher
    #         where wht_period_id = %s and income_tax_form = %s
    #     """, (wht_period_id, income_tax_form))
    #     next_sequence = self._cr.fetchone()[0]
    #     return next_sequence

    @api.model
    def _get_seq_search_domain(self, income_tax_form, wht_period):
        domain = [('income_tax_form', '=', income_tax_form),
                  ('period_id', '=', wht_period.id)]
        return domain

    @api.model
    def _get_next_wht_sequence(self, income_tax_form, wht_period):
        Sequence = self.env['ir.sequence']
        WHTSequence = self.env['withholding.tax.sequence']
        domain = self._get_seq_search_domain(income_tax_form, wht_period)
        seq = WHTSequence.search(domain, limit=1)
        if not seq:
            seq = self._create_sequence(income_tax_form, wht_period)
        return int(Sequence.next_by_id(seq.sequence_id.id))

    @api.model
    def _get_seq_name(self, income_tax_form, wht_period):
        name = 'WHT-%s-%s' % (income_tax_form, wht_period.code,)
        return name

    @api.model
    def _prepare_wht_seq(self, income_tax_form, wht_period, new_sequence):
        vals = {
            'income_tax_form': income_tax_form,
            'period_id': wht_period.id,
            'sequence_id': new_sequence.id,
        }
        return vals

    @api.model
    def _create_sequence(self, income_tax_form, wht_period):
        seq_vals = {'name': self._get_seq_name(income_tax_form, wht_period),
                    'implementation': 'no_gap'}
        new_sequence = self.env['ir.sequence'].create(seq_vals)
        vals = self._prepare_wht_seq(income_tax_form, wht_period, new_sequence)
        return self.env['withholding.tax.sequence'].create(vals)


class WithholdingTaxSequence(models.Model):
    _name = 'withholding.tax.sequence'
    _description = 'Keep track of WHT sequences'
    _rec_name = 'period_id'

    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        readonly=True,
        help="Specify form for withholding tax, default with setup in supplier"
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Sequence',
        ondelete='restrict',
    )
    number_next_actual = fields.Integer(
        string='Next Number',
        related='sequence_id.number_next_actual',
        readonly=True,
    )


class AccountVoucherLine(common_voucher, models.Model):

    _inherit = 'account.voucher.line'

    amount_wht = fields.Float(
        string='WHT',
        digits_compute=dp.get_precision('Account'))
    amount_retention = fields.Float(
        string='Retention',
        digits_compute=dp.get_precision('Account'))
    retention_on_payment = fields.Boolean(
        string='Retention on Payment',
        related='move_line_id.invoice.retention_on_payment',
        store=True,
        readonly=True)

    @api.model
    def _get_amount_wht(self, partner_id, move_line_id,
                        amount_original, amount):
        tax_obj = self.env['account.tax']
        partner_obj = self.env['res.partner']
        move_line_obj = self.env['account.move.line']
        partner = partner_obj.browse(partner_id)
        move_line = move_line_obj.browse(move_line_id)
        amount_wht = 0.0
        if move_line.invoice:
            invoice = move_line.invoice
            for line in invoice.invoice_line:
                revised_price = (line.price_unit *
                                 (1 - (line.discount or 0.0) / 100.0))
                # Only WHT
                is_wht = True in [x.is_wht
                                  for x in
                                  line.invoice_line_tax_id] or False
                if is_wht:
                    ratio = (float(amount_original) and
                             (float(amount) / float(amount_original)) or 0.0)
                    tax_list = line.invoice_line_tax_id.compute_all(
                        float(revised_price) * ratio,
                        line.quantity,
                        line.product_id,
                        partner)['taxes']
                    for tax in tax_list:
                        account_tax = tax_obj.browse(tax['id'])
                        if account_tax.is_wht:
                            amount_wht += tax['amount']

            # Change to currency at invoicing time.
            amount_wht = self._to_voucher_currency(invoice,
                                                   move_line.journal_id,
                                                   amount_wht,)
        return float(amount), float(amount_wht)

    @api.model
    def _get_amount_retention(self, partner_id,
                              move_line_id, amount_original, amount):
        move_line_obj = self.env['account.move.line']
        move_line = move_line_obj.browse(move_line_id)
        amount_retention = 0.0
        if move_line.invoice:
            invoice = move_line.invoice
            if invoice.retention_on_payment:
                ratio = (float(amount_original) and
                         (float(amount) / float(amount_original)) or 0.0)
                amount_retention = invoice.amount_retention * ratio
                # Change to currency at invoicing time.
                amount_retention = self._to_voucher_currency(
                    invoice,
                    move_line.journal_id,
                    amount_retention)
        return float(amount), float(amount_retention)

    @api.multi
    def onchange_amount(self, partner_id, move_line_id,
                        amount_original, amount, amount_unreconciled):
        vals = {}
        prec = self.env['decimal.precision'].precision_get('Account')
        amount, amount_wht = self._get_amount_wht(
            partner_id,
            move_line_id,
            amount_original,
            amount)
        amount, amount_retention = self._get_amount_retention(
            partner_id,
            move_line_id,
            amount_original,
            amount)
        vals['amount_wht'] = -round(amount_wht, prec)
        vals['amount_retention'] = -round(amount_retention, prec)
        vals['reconcile'] = (round(amount) == round(amount_unreconciled))
        return {'value': vals}

    @api.multi
    def onchange_reconcile(self, partner_id, move_line_id, amount_original,
                           reconcile, amount, amount_unreconciled):
        vals = {}
        prec = self.env['decimal.precision'].precision_get('Account')
        if reconcile:
            amount = amount_unreconciled
            amount, amount_wht = self._get_amount_wht(
                partner_id,
                move_line_id,
                amount_original,
                amount)
            amount, amount_retention = self._get_amount_retention(
                partner_id,
                move_line_id,
                amount_original,
                amount)
            vals['amount_wht'] = -round(amount_wht, prec)
            vals['amount_retention'] = -round(amount_retention, prec)
            vals['amount'] = round(amount, prec)
        return {'value': vals}


class AccountVoucherTax(common_voucher, models.Model):

    _name = "account.voucher.tax"
    _description = "Voucher Tax"
    _order = 'sequence,invoice_id,name'

    @api.one
    @api.depends('tax_amount', 'amount')
    def _count_factor(self):
        self.factor_tax = (self.amount != 0.0 and
                           self.tax_amount / self.amount or 1.0)
        self.factor_base = (self.base != 0.0 and
                            self.base_amount / self.base or 1.0)

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        ondelete='cascade',
        index=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )
    tax_id = fields.Many2one(
        'account.tax',
        string='Tax',
    )
    name = fields.Char(
        string='Tax Description',
        size=64,
        required=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Tax Account',
        required=True,
        domain=[('type', 'not in', ('view', 'income', 'closed'))],
    )
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic account',
    )
    base = fields.Float(
        string='Base',
        digits_compute=dp.get_precision('Account'),
    )
    amount = fields.Float(
        string='Amount',
        digits_compute=dp.get_precision('Account'),
    )
    tax_currency_gain = fields.Float(
        string='Currency Gain',
        digits_compute=dp.get_precision('Account'),
    )
    manual = fields.Boolean(
        string='Manual',
        default=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        help="Sequence order when displaying a list of voucher tax.",
    )
    base_code_id = fields.Many2one(
        'account.tax.code',
        string='Base Code',
        help="The account basis of the tax declaration.",
    )
    base_amount = fields.Float(
        string='Base Code Amount',
        digits_compute=dp.get_precision('Account'),
        default=0.0,
    )
    tax_code_id = fields.Many2one(
        'account.tax.code',
        string='Tax Code',
        help="The tax basis of the tax declaration.",
    )
    tax_code_type = fields.Selection(
        [('normal', 'Normal'),
         ('undue', 'Undue'),
         ('wht', 'Withholding')],
        string='Tax Code Type',
        related='tax_code_id.tax_code_type',
        store=True,
        help="Type based on Tax using this Tax Code",
    )
    tax_amount = fields.Float(
        string='Tax Code Amount',
        digits_compute=dp.get_precision('Account'),
        default=0.0,
    )
    company_id = fields.Many2one(
        'res.company',
        related='account_id.company_id',
        string='Company',
        store=True,
        readonly=True,
    )
    factor_base = fields.Float(
        string='Multipication factor for Base code',
        compute='_count_factor',
    )
    factor_tax = fields.Float(
        string='Multipication factor Tax code',
        compute='_count_factor',
    )
    wht_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
    )

    @api.model
    def _compute_one_tax_grouped(self, taxes, voucher, voucher_cur,
                                 invoice, invoice_cur, company_currency,
                                 journal, line_sign, payment_ratio,
                                 line, revised_price):
        tax_gp = {}
        tax_obj = self.env['account.tax']

        for tax in taxes:
            # For Normal
            val = {}
            val['voucher_id'] = voucher.id
            val['invoice_id'] = invoice.id
            val['tax_id'] = tax['id']
            val['name'] = tax['name']
            val['amount'] = self._to_voucher_currency(
                invoice, journal,
                (tax['amount'] *
                 payment_ratio *
                 line_sign))
            val['manual'] = False
            val['sequence'] = tax['sequence']
            val['base'] = self._to_voucher_currency(
                invoice, journal,
                voucher_cur.round(
                    tax['price_unit'] * line.quantity) *
                payment_ratio * line_sign)
            # For Undue
            vals = {}
            vals['voucher_id'] = voucher.id
            vals['invoice_id'] = invoice.id
            vals['tax_id'] = tax['id']
            vals['name'] = tax['name']
            vals['amount'] = self._to_invoice_currency(
                invoice, journal,
                (-tax['amount'] *
                 payment_ratio *
                 line_sign))
            vals['manual'] = False
            vals['sequence'] = tax['sequence']
            vals['base'] = self._to_invoice_currency(
                invoice, journal,
                voucher_cur.round(
                    -tax['price_unit'] * line.quantity) *
                payment_ratio * line_sign)

            # Register Currency Gain for Normal
            val['tax_currency_gain'] = -(val['amount'] + vals['amount'])
            vals['tax_currency_gain'] = 0.0

            # Check the if services, which has been using undue account
            # This time, it needs to cr: non-undue acct and dr: undue acct
            tax1 = tax_obj.browse(tax['id'])
            is_wht = tax1.is_wht
            # -------------------> Adding Tax for Posting
            if is_wht:
                # Check Threshold first
                base = invoice_cur.compute((revised_price * line.quantity),
                                           company_currency)
                t = tax_obj.browse(val['tax_id'])
                if abs(base) and abs(base) < t.threshold_wht:
                    continue
                # For WHT, change sign.
                val['base'] = -val['base']
                val['amount'] = -val['amount']
                # Case Withholding Tax Dr.
                if voucher.type in ('receipt', 'payment'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['base_sign'],
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['tax_sign'],
                        company_currency) * payment_ratio
                    val['account_id'] = (tax['account_collected_id'] or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['ref_base_sign'],
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['ref_tax_sign'],
                        company_currency) * payment_ratio
                    val['account_id'] = (tax['account_paid_id'] or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        tax['account_analytic_paid_id']

                if not val.get('account_analytic_id', False) and \
                        line.account_analytic_id and \
                        val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['invoice_id'], val['tax_code_id'],
                       val['base_code_id'], val['account_id'])
                if not (key in tax_gp):
                    tax_gp[key] = val
                    tax_gp[key]['amount'] = tax_gp[key]['amount']
                    tax_gp[key]['base'] = tax_gp[key]['base']
                    tax_gp[key]['base_amount'] = tax_gp[key]['base_amount']
                    tax_gp[key]['tax_amount'] = tax_gp[key]['tax_amount']
                    tax_gp[key]['tax_currency_gain'] = 0.0  # No gain for WHT
                else:
                    tax_gp[key]['amount'] += val['amount']
                    tax_gp[key]['base'] += val['base']
                    tax_gp[key]['base_amount'] += val['base_amount']
                    tax_gp[key]['tax_amount'] += val['tax_amount']
                    tax_gp[key]['tax_currency_gain'] += 0.0  # No gain for WHT

            # --> Adding Tax for Posting 1) Contra-Undue 2) Non-Undue
            elif tax1.is_undue_tax:
                # First: Do the Cr: with Non-Undue Account
                refer_tax = tax1.refer_tax_id
                if not refer_tax:
                    raise ValidationError(
                        _('Undue Tax require Counterpart Tax when setup'))
                # Change name to refer_tax_id
                val['name'] = refer_tax.name
                if voucher.type in ('receipt', 'payment'):
                    val['tax_id'] = refer_tax and refer_tax.id or val['tax_id']
                    val['base_code_id'] = refer_tax.base_code_id.id
                    val['tax_code_id'] = refer_tax.tax_code_id.id
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        refer_tax.base_sign,
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        refer_tax.tax_sign,
                        company_currency) * payment_ratio
                    val['account_id'] = (refer_tax.account_collected_id.id or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        refer_tax.account_analytic_collected_id.id
                else:
                    val['tax_id'] = refer_tax and refer_tax.id or val['tax_id']
                    val['base_code_id'] = refer_tax.ref_base_code_id.id
                    val['tax_code_id'] = refer_tax.ref_tax_code_id.id
                    val['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        refer_tax.ref_base_sign,
                        company_currency) * payment_ratio
                    val['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        refer_tax.ref_tax_sign,
                        company_currency) * payment_ratio
                    val['account_id'] = (refer_tax.account_paid_id.id or
                                         line.account_id.id)
                    val['account_analytic_id'] = \
                        refer_tax.account_analytic_paid_id.id

                if not val.get('account_analytic_id', False) and \
                        line.account_analytic_id and \
                        val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['invoice_id'], val['tax_code_id'],
                       val['base_code_id'], val['account_id'])
                if not (key in tax_gp):
                    tax_gp[key] = val
                else:
                    tax_gp[key]['amount'] += val['amount']
                    tax_gp[key]['base'] += val['base']
                    tax_gp[key]['base_amount'] += val['base_amount']
                    tax_gp[key]['tax_amount'] += val['tax_amount']
                    tax_gp[key]['tax_currency_gain'] += \
                        val['tax_currency_gain']

                # Second: Do the Dr: with Undue Account
                if voucher.type in ('receipt', 'payment'):
                    vals['base_code_id'] = tax['base_code_id']
                    vals['tax_code_id'] = tax['tax_code_id']
                    vals['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['base_sign'],
                        company_currency) * payment_ratio
                    vals['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['tax_sign'],
                        company_currency) * payment_ratio
                    # USE UNDUE ACCOUNT HERE
                    vals['account_id'] = \
                        (tax1.account_collected_id.id or
                         line.account_id.id)
                    vals['account_analytic_id'] = \
                        tax['account_analytic_collected_id']
                else:
                    vals['base_code_id'] = tax['ref_base_code_id']
                    vals['tax_code_id'] = tax['ref_tax_code_id']
                    vals['base_amount'] = voucher_cur.compute(
                        val['base'] *
                        tax['ref_base_sign'],
                        company_currency) * payment_ratio
                    vals['tax_amount'] = voucher_cur.compute(
                        val['amount'] *
                        tax['ref_tax_sign'],
                        company_currency) * payment_ratio
                    # USE UNDUE ACCOUNT HERE
                    vals['account_id'] = \
                        (tax1.account_paid_id.id or
                         line.account_id.id)
                    vals['account_analytic_id'] = \
                        tax['account_analytic_paid_id']

                if not vals.get('account_analytic_id') and \
                        line.account_analytic_id and \
                        vals['account_id'] == line.account_id.id:
                    vals['account_analytic_id'] = line.account_analytic_id.id

                key = (vals['invoice_id'], vals['tax_code_id'],
                       vals['base_code_id'], vals['account_id'])

                if not (key in tax_gp):
                    tax_gp[key] = vals
                else:
                    tax_gp[key]['amount'] += vals['amount']
                    tax_gp[key]['base'] += vals['base']
                    tax_gp[key]['base_amount'] += vals['base_amount']
                    tax_gp[key]['tax_amount'] += vals['tax_amount']
                    tax_gp[key]['tax_currency_gain'] += \
                        vals['tax_currency_gain']
                    # ------------------------------------------------
        return tax_gp

    @api.model
    def _compute_tax_grouped(self, voucher, voucher_line,
                             voucher_cur, line_sign):
        invoice = voucher_line.move_line_id.invoice
        journal = voucher_line.voucher_id.journal_id
        payment_ratio = (voucher_line.amount_original and
                         (voucher_line.amount /
                          (voucher_line.amount_original or 1)) or
                         0.0)
        date = invoice.date_invoice or fields.Date.context_today(invoice)
        invoice_cur = invoice.currency_id.with_context(date=date)
        company_currency = invoice.company_id.currency_id
        # Retrieve Additional Discount, Advance and Deposit in percent.
        tax_gps = {}
        for line in voucher_line.move_line_id.invoice.invoice_line:
            # Each invoice line, calculate tax
            revised_price = line.price_unit * (1 - (line.discount / 100.0))
            taxes = line.invoice_line_tax_id.compute_all(
                revised_price,
                line.quantity,
                line.product_id,
                invoice.partner_id)['taxes']
            tax_gp = self._compute_one_tax_grouped(
                taxes, voucher, voucher_cur, invoice,
                invoice_cur, company_currency,
                journal, line_sign, payment_ratio,
                line, revised_price)
            # Grouping
            for key in tax_gp:
                if key not in tax_gps.keys():
                    tax_gps[key] = tax_gp[key]
                else:
                    tax_gps[key]['tax_currency_gain'] += \
                        tax_gp[key]['tax_currency_gain']
                    tax_gps[key]['tax_amount'] += tax_gp[key]['tax_amount']
                    tax_gps[key]['base_amount'] += tax_gp[key]['base_amount']
                    tax_gps[key]['amount'] += tax_gp[key]['amount']
                    tax_gps[key]['base'] += tax_gp[key]['base']

        return tax_gps

    @api.model
    def compute(self, voucher):
        tax_gps = {}
        tax_gp = {}
        date = voucher.date or fields.Date.context_today(voucher)
        voucher_cur = voucher.currency_id.with_context(date=date)
        for voucher_line in voucher.line_ids:
            line_sign = 1
            if voucher.type in ('sale', 'receipt'):
                line_sign = voucher_line.type == 'cr' and 1 or -1
            elif voucher.type in ('purchase', 'payment'):
                line_sign = voucher_line.type == 'dr' and 1 or -1
            # Each voucher line is equal to an invoice,
            # we will need to go through all of them.
            if voucher_line.move_line_id.invoice:
                tax_gp = self._compute_tax_grouped(voucher, voucher_line,
                                                   voucher_cur, line_sign)
                # Grouping into tax_gps
                for key in tax_gp:
                    if key not in tax_gps.keys():
                        tax_gps[key] = tax_gp[key]
                    else:
                        tax_gps[key]['tax_currency_gain'] += \
                            tax_gp[key]['tax_currency_gain']
                        tax_gps[key]['tax_amount'] += tax_gp[key]['tax_amount']
                        tax_gps[key]['base_amount'] += \
                            tax_gp[key]['base_amount']
                        tax_gps[key]['amount'] += tax_gp[key]['amount']
                        tax_gps[key]['base'] += tax_gp[key]['base']
        # rounding
        for t in tax_gps.values():
            t['base'] = voucher_cur.round(t['base'])
            t['amount'] = voucher_cur.round(t['amount'])
            t['base_amount'] = voucher_cur.round(t['base_amount'])
            t['tax_amount'] = voucher_cur.round(t['tax_amount'])
            t['tax_currency_gain'] = voucher_cur.round(t['tax_currency_gain'])

        return tax_gps

    @api.model
    def _prepare_one_move_line(self, t):
        return {
            'type': 'tax',
            'name': t['name'],
            'price_unit': t['amount'],
            'quantity': 1,
            'price': t['amount'] or 0.0,
            'tax_currency_gain': t['tax_currency_gain'] or 0.0,
            'account_id': t['account_id'],
            'tax_code_id': t['tax_code_id'],
            'tax_amount': t['tax_amount'],
            'account_analytic_id': t['account_analytic_id'],
            'tax_code_type': t['tax_code_type'],
            'invoice_id': t['invoice_id'],  # pass for future use
        }

    @api.model
    def move_line_get(self, voucher):
        res = []
        sql = "SELECT * FROM account_voucher_tax WHERE voucher_id=%s"
        # For Supplier Invoice only, check 2step posting
        if voucher.type == 'payment':
            if not self.env.user.company_id.auto_recognize_vat:
                # Step 2 for normal and undue
                if self._context.get('recognize_vat', False):
                    sql += " and tax_code_type != 'wht' "
                else:
                    sql += " and tax_code_type = 'wht' "
        self._cr.execute(sql, (voucher.id,))
        for t in self._cr.dictfetchall():
            if not t['amount']:
                continue
            res.append(self._prepare_one_move_line(t))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
