# -*- coding: utf-8 -*-
import ast
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare


class LoanInstallment(models.Model):
    _name = 'loan.installment'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'Convert trade receivable to loan installment receivable'

    name = fields.Char(
        string='Loan Installment Number',
        required=True,
        readonly=True,
        default='/',
    )
    date = fields.Date(
        string='Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain=[('customer', '=', True)],
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    receivable_ids = fields.Many2many(
        'account.move.line',
        'loan_installment_move_line_rel',
        'loan_install_id', 'move_line_id',
        string='Trade Receivables',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('state','=','valid'),"
        "('account_id.type', '=', 'receivable'),"
        "('reconcile_id', '=', False),"
        "('partner_id', '=', partner_id),"
        "('account_id', '!=', account_id)]",
    )
    # income_ids = fields.One2many(
    #     'loan.installment.income',
    #     'loan_install_id',
    #     string='Additional Income',
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    # )
    amount_loan_total = fields.Float(
        string='Loan Amount',
        compute='_compute_amount',
        store=True,
    )
    amount_receivable = fields.Float(
        string='Receivables',
        compute='_compute_amount',
        store=True,
    )
    amount_income = fields.Float(
        string='Incomes',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        readonly=True,
        default=lambda self: self.env.ref('pabi_account_move_adjustment.'
                                          'journal_adjust_budget'),
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
        readonly=True,
        default=lambda self:
        self.env.user.company_id.loan_installment_account_id,
    )
    defer_income_account_id = fields.Many2one(
        'account.account',
        string='Defer Income Account',
        required=True,
        readonly=True,
        default=lambda self:
        self.env.user.company_id.loan_defer_income_account_id,
    )
    income_account_id = fields.Many2one(
        'account.account',
        string='Income Account',
        required=True,
        readonly=True,
        default=lambda self:
        self.env.user.company_id.loan_income_account_id,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
    )
    cancel_move_id = fields.Many2one(
        'account.move',
        string='Cancel Entry',
        readonly=True,
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Sales Orer',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Coverted to Loan'),
         ('paid', 'Fully Paid'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    is_paid = fields.Boolean(
        string='Fully Paid',
        compute='_compute_is_paid',
        store=True,
        track_visibility='onchange',
    )
    # Compute installment table
    date_start = fields.Date(
        string='1st Installment Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    period_type = fields.Selection(
        [('day', 'days'),
         ('month', 'month'),
         ('year', 'year')],
        string='Period Type',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='month',
    )
    consider_month_end = fields.Boolean(
        string='Consider Month End',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    period_nbr = fields.Integer(
        string='Period',
        default=1,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    period_total = fields.Integer(
        string='Number of Periods',
        default=12,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    rate_type = fields.Selection(
        [('daily', 'Daily'),
         ('monthly', 'Monthly'),
         ('yearly', 'Yearly'),
         ],
        string='Rate',
        default='monthly',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    rate = fields.Float(
        string='Rate',
        compute='_compute_rate',
    )
    rate_err_message = fields.Char(
        string='Error Message',
    )
    installment_ids = fields.One2many(
        'loan.installment.plan',
        'loan_install_id',
        string='Installment Plan',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    _sql_constraints = [
        ('name_unique', 'unique(name)',
         'Loan installment number must be unique!'),
    ]

    @api.multi
    @api.depends('move_id.line_id.reconcile_id')
    def _compute_is_paid(self):
        MoveLine = self.env['account.move.line']
        account_types = ['receivable', 'payable']
        for rec in self:
            if not rec.move_id:
                rec.is_paid = False
                continue
            # Move created, find whether all are paid.
            unreconcile_line_ids = MoveLine.search([
                ('move_id', '=', rec.move_id.id),
                ('state', '=', 'valid'),
                ('account_id.type', 'in', account_types),
                ('reconcile_id', '=', False)])._ids
            if not unreconcile_line_ids:
                rec.is_paid = True
            else:
                rec.is_paid = False

    @api.multi
    def _write(self, vals):
        """ As is_paid is triggered, so do the state """
        for rec in self:
            if 'is_paid' in vals:
                if rec.state == 'open' and vals['is_paid'] is True:
                    vals['state'] = 'paid'
                if rec.state == 'paid' and vals['is_paid'] is False:
                    vals['state'] = 'open'
        return super(LoanInstallment, self)._write(vals)

    @api.multi
    def open_account_move(self):
        self.ensure_one()
        return {
            'name': _("Journal Entries"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'nodestroy': True,
            'domain': [('id', '=', [self.move_id.id, self.cancel_move_id.id])],
        }

    @api.multi
    def action_open_payments(self):
        self.ensure_one()
        move_line_ids = self.installment_ids.mapped('move_line_id').ids
        Voucher = self.env['account.voucher']
        vouchers = Voucher.search(
            [('line_ids.move_line_id', 'in', move_line_ids),
             ('state', '=', 'posted')])
        action = self.env.ref('account_voucher.action_vendor_payment')
        if not action:
            raise ValidationError(_('No Action'))
        action = action.read([])[0]
        action['domain'] = [('id', 'in', vouchers.ids)]
        return action

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.receivable_ids = False
        self.amount_income = 0.0
        # self.income_ids = False

    @api.multi
    @api.depends('receivable_ids', 'amount_income')
    def _compute_amount(self):
        for rec in self:
            # rec.amount_income = sum(rec.income_ids.mapped('amount'))
            rec.amount_receivable = \
                sum(rec.receivable_ids.mapped(lambda l: l.debit - l.credit))
            rec.amount_loan_total = rec.amount_income + rec.amount_receivable

    @api.model
    def create(self, vals):
        sequence_code = 'loan.installment'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        res = super(LoanInstallment, self).create(vals)
        return res

    @api.multi
    def loan_move_line_get(self, line):
        self.ensure_one()
        move_line = {
            'move_id': self.move_id.id,
            'name': '%s #%s' % (self.name, line.installment),
            'debit': line.amount > 0.0 and line.amount or 0.0,
            'credit': line.amount < 0.0 and line.amount or 0.0,
            'account_id': self.account_id.id,
            'partner_id': self.partner_id.id,
            'date_maturity': line.date_start,
        }
        return move_line

    # @api.multi
    # def _prepare_income_move_lines(self):
    #     self.ensure_one()
    #     move_line_dict = []
    #     for line in self.income_ids:
    #         line_dict = self.move_line_get_item(line)
    #         move_line_dict.append((0, 0, line_dict))
    #     return move_line_dict

    @api.multi
    def _prepare_income_move_line(self):
        self.ensure_one()
        move_line_dict = {
            'move_id': self.move_id.id,
            'date': self.date,
            'date_maturity': False,
            'name': self.defer_income_account_id.name or '/',
            'partner_id': self.partner_id.id,
            'account_id': self.defer_income_account_id.id,
            'analytic_account_id': False,
            'debit': self.amount_income < 0 and -self.amount_income or 0.0,
            'credit': self.amount_income > 0 and self.amount_income or 0.0,
        }
        return move_line_dict

    # @api.multi
    # def move_line_get_item(self, line):
    #     self.ensure_one()
    #     return {
    #         'date': line.date,
    #         'date_maturity': False,
    #         'name': line.name or '/',
    #         'partner_id': line.partner_id.id,
    #         'account_id': line.account_id.id,
    #         'analytic_account_id': False,
    #         'debit': line.amount < 0 and -line.amount or 0.0,
    #         'credit': line.amount > 0 and line.amount or 0.0,
    #     }

    @api.multi
    def _validate(self):
        for rec in self:
            if not rec.receivable_ids:
                raise ValidationError(_('No trade receivable line selected!'))
            install_amount = sum(rec.installment_ids.mapped('amount'))
            if float_compare(install_amount, rec.amount_loan_total, 2) != 0:
                raise ValidationError(_('Please calculate installment plan!'))

    @api.multi
    def _cancel(self):
        self.ensure_one()
        period = self.env['account.period'].find()
        move = self.move_id
        AccountMove = self.env['account.move']
        move_dict = move.copy_data({
            'name': move.name + '_VOID',
            'ref': move.ref,
            'period_id': period.id,
            'date': fields.Date.context_today(self), })[0]
        move_dict = AccountMove._switch_move_dict_dr_cr(move_dict)
        rev_move = AccountMove.create(move_dict)
        # Delete reconcile, and receconcile with reverse entry
        move.line_id.filtered('reconcile_id').reconcile_id.unlink()
        accounts = move.line_id.mapped('account_id')
        for account in accounts:
            AccountMove.\
                _reconcile_voided_entry_by_account([move.id, rev_move.id],
                                                   account.id)
        self.cancel_move_id = rev_move

    @api.multi
    def action_cancel(self):
        for rec in self:
            if not rec.move_id:
                continue
            if rec.installment_ids.mapped('reconcile_id'):
                raise ValidationError(
                    _('Some installment was paid, cancllation not allowed!'))
            rec._cancel()
        self.write({'state': 'cancel'})

    @api.multi
    def action_move_create(self):
        self._validate()
        Move = self.env['account.move']
        MoveLine = self.env['account.move.line']
        # Analytic = self.env['account.analytic.account']
        # # Update dimensions
        # for rec in self:
        #     for line in rec.income_ids:
        #         line.analytic_account_id = \
        #             Analytic.create_matched_analytic(line)
        # # --
        for rec in self:
            if rec.move_id:
                continue
            move_dict = Move.account_move_prepare(rec.journal_id.id,
                                                  date=rec.date, ref=rec.name)
            move = Move.create(move_dict)
            rec.move_id = move
            # Dr ลูกหนี้ผ่อนชำระ
            for line in self.installment_ids:
                move_line_dict = self.loan_move_line_get(line)
                loan_move_line = MoveLine.create(move_line_dict)
                line.move_line_id = loan_move_line
            # --
            rec_pair_ids = []
            # Receivables to be reconciled
            for move_line in rec.receivable_ids:
                # Prepare line used to recconile with receivable_ids
                move_line_dict = move_line.copy_data()[0]
                debit = move_line_dict['debit']
                credit = move_line_dict['credit']
                move_line_dict.update({'move_id': move.id,
                                       'debit': credit, 'credit': debit})
                rec_move_line = MoveLine.create(move_line_dict)
                # --
                rec_pair_ids.append([move_line.id, rec_move_line.id])
            # Extra Defer Income.
            income_line = rec._prepare_income_move_line()
            MoveLine.create(income_line)
            # Post move
            move.with_context(direct_create=True).button_validate()
            # Reconcile receivables
            for rec_ids in rec_pair_ids:
                MoveLine.browse(rec_ids).reconcile('auto')
        # Done
        self.write({'state': 'open'})
        return True

    @api.model
    def _get_date_last(self, sub):
        date_last = datetime.strptime(sub.date_start, '%Y-%m-%d')
        periods = sub.period_nbr * sub.period_total
        if sub.period_type == 'day':
            date_last += relativedelta(days=periods)
        if sub.period_type == 'month':
            date_last += relativedelta(months=periods)
        if sub.period_type == 'year':
            date_last += relativedelta(years=periods)
        return date_last

    @api.multi
    def compute(self):
        for rec in self:
            ds = rec.date_start
            date_start = datetime.strptime(ds, '%Y-%m-%d')
            date_last = self._get_date_last(rec)
            i = 0
            install_lines = []
            while i < rec.period_total:
                line = {
                    'installment': i + 1,
                    'date_start': date_start.strftime('%Y-%m-%d'),
                    'loan_install_id': rec.id,
                }
                # Consider month end
                if self.consider_month_end:
                    if date_start.day != 1:
                        date_start = datetime.strptime(
                            date_start.strftime('%Y-%m-01'), '%Y-%m-%d')
                        i -= 1
                # --
                if rec.period_type == 'day':
                    date_start = \
                        date_start + relativedelta(days=rec.period_nbr)
                if rec.period_type == 'month':
                    date_start = \
                        date_start + relativedelta(months=rec.period_nbr)
                if rec.period_type == 'year':
                    date_start = \
                        date_start + relativedelta(years=rec.period_nbr)
                i += 1
                if i == rec.period_total:
                    line['date_end'] = date_last - relativedelta(days=1)
                else:
                    line['date_end'] = date_start - relativedelta(days=1)
                install_lines.append((0, 0, line))
            rec.write({'installment_ids': install_lines})
        return True

    @api.multi
    @api.depends('amount_loan_total', 'rate_type')
    def _compute_rate(self):
        for rec in self:
            rec.rate_err_message = False
            if not rec.installment_ids:
                continue
            date_min = min(rec.installment_ids.mapped('date_start'))
            date_max = max(rec.installment_ids.mapped('date_end'))
            if not date_min or not date_max:
                rec.rate = 0.0
                continue
            date_start = datetime.strptime(date_min, '%Y-%m-%d')
            date_end = datetime.strptime(date_max, '%Y-%m-%d') + \
                relativedelta(days=1)
            days = (date_end - date_start).days
            r = relativedelta(date_end, date_start)
            if rec.rate_type == 'daily':
                rec.rate = rec.amount_loan_total / days
            elif rec.rate_type == 'monthly':
                if r.days:
                    rec.rate_err_message = \
                        _('Cannot calculate monthly rate, days residual!')
                    rec.rate = 0.0
                    continue
                rec.rate = rec.amount_loan_total / (r.years * 12 + r.months)
            elif rec.rate_type == 'yearly':
                if r.days or r.months:
                    rec.rate_err_message = \
                        _('Cannot calculate yearly rate, '
                          'months/days residual!')
                    rec.rate = 0.0
                    continue
                rec.rate = rec.amount_loan_total / r.years
        return

    @api.multi
    def calculate_installment(self):
        # Remove lines
        for rec in self:
            rec.installment_ids.unlink()
        # Compute
        for rec in self:
            rec.compute()
        # Fill Installment
        for rec in self:
            if not rec.rate_type or not rec.rate:
                continue
            num_line = len(rec.installment_ids)
            sum_amount = 0.0
            i = 0
            while i < num_line:
                line = rec.installment_ids[i]
                date_start = datetime.strptime(line.date_start, '%Y-%m-%d')
                date_end = datetime.strptime(line.date_end, '%Y-%m-%d') + \
                    relativedelta(days=1)
                days = (date_end - date_start).days
                r = relativedelta(date_end, date_start)
                if rec.rate_type == 'daily':
                    line.amount = round(days * rec.rate, 2)
                if rec.rate_type == 'monthly':
                    line.amount = \
                        round((r.years * 12 + r.months) * rec.rate, 2)
                if rec.rate_type == 'yearly':
                    line.amount = round(r.years * rec.rate, 2)
                sum_amount += line.amount
                i += 1
                if i == num_line:
                    line.amount = \
                        (rec.amount_loan_total - sum_amount) + line.amount
        return

    @api.multi
    def action_create_payment(self, installment_ids=False):
        action_id = False
        action_id = self.env.ref('account_voucher.action_vendor_receipt')
        if not action_id:
            raise ValidationError(_('No Action'))
        action = action_id.read([])[0]
        ctx = ast.literal_eval(action['context'])
        ctx.update({
            'filter_loans': self.ids,
            'filter_loan_installments': installment_ids,
        })
        action['context'] = ctx
        action['views'].reverse()
        return action


# class LoanInstallmentIncome(models.Model):
#     _name = 'loan.installment.income'
#
#     loan_install_id = fields.Many2one(
#         'loan.installment',
#         string='Loan Installment',
#         index=True,
#         ondelete='cascade',
#         readonly=True,
#     )
#     name = fields.Char(
#         string='Description',
#     )
#     date = fields.Date(
#         string='Date',
#         related='loan_install_id.date',
#         readonly=True,
#     )
#     partner_id = fields.Many2one(
#         'res.partner',
#         string='Customer',
#         related='loan_install_id.partner_id',
#         readonly=True,
#     )
#     account_id = fields.Many2one(
#         'account.account',
#         string='Account',
#         domain=[('type', '=', 'other'),
#                 ('user_type.report_type', '=', 'liability')],
#         required=True,
#         default=lambda self: self.env.user.company_id.loan_income_account_id,
#     )
#     amount = fields.Float(
#         string='Amount',
#         required=True,
#         default=0.0,
#     )


class LoanInstallmentPlan(models.Model):
    _name = 'loan.installment.plan'
    _rec_name = 'installment'

    loan_install_id = fields.Many2one(
        'loan.installment',
        string='Loan Installment',
        index=True,
        ondelete='cascade',
        readonly=True,
    )
    installment = fields.Integer(
        string='Installment',
        readonly=True,
    )
    date_start = fields.Date(
        string='Start Date',
        readonly=True,
    )
    date_end = fields.Date(
        string='End Date',
        readonly=True,
    )
    days = fields.Integer(
        string='Days',
        compute='_compute_days',
    )
    income = fields.Float(
        string='Income',
        compute='_compute_income',
    )
    amount = fields.Float(
        string='Amount',
        default=0.0,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item',
        readonly=True,
    )
    reconcile_id = fields.Many2one(
        'account.move.reconcile',
        related='move_line_id.reconcile_id',
        string='Reconcile',
        readonly=True,
    )

    @api.multi
    def name_get(self):
        res = []
        for rec in self.sorted(key=lambda l: (l.loan_install_id,
                                              l.installment)):
            name = '%s #%s' % \
                (rec.loan_install_id.name, rec.installment)
            res.append((rec.id, name))
        return res

    @api.multi
    def _compute_days(self):
        prev_start = False
        for rec in self.sorted(key=lambda self: self.date_start):
            date_start = fields.Date.from_string(rec.date_start)
            rec.days = prev_start and (date_start - prev_start).days or 0
            prev_start = date_start

    @api.multi
    def _compute_income(self):
        for rec in self:
            total_income = rec.loan_install_id.amount_income
            total_loan = rec.loan_install_id.amount_loan_total
            if not total_loan:
                rec.income = 0.0
            else:
                rec.income = (total_income / total_loan) * rec.amount
