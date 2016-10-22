# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError, ValidationError
from openerp.tools import float_compare
import datetime


class PersonalIncomeTax(models.Model):
    _name = 'personal.income.tax'
    _description = 'Personal Income Tax'

    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        index=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)],
        index=True,
        required=True,
        ondelete='cascade',
    )
    date = fields.Date(
        string='Date',
        related='voucher_id.date',
        store=True,
        readonly=True,
    )
    calendar_year = fields.Char(
        string='Calendar Year',
        compute='_compute_calendar_year',
        store=True,
        readonly=True,
    )
    amount_income = fields.Float(
        string='Income',
        required=True,
        default=lambda self: self._default_amount_income()
    )
    amount_wht = fields.Float(
        string='Withholding Amount',
        required=True,
    )
    posted = fields.Boolean(
        string='Posted',
        compute='_compute_posted',
        store=True,
        readonly=True,
    )
    _sql_constraints = [
        ('pit_uniq', 'unique (voucher_id, partner_id)',
         'Duplicated supplier on PIT!'),
    ]

    @api.model
    def _default_amount_income(self):
        income = 0.0
        voucher_id = self._context.get('voucher_id', False)
        if voucher_id:
            voucher = self.env['account.voucher'].browse(voucher_id)
            income += (sum([x.amount for x in voucher.line_dr_ids]) -
                       sum([x.amount for x in voucher.line_cr_ids]))
        else:
            ctx = self._context.copy()
            income += (sum([x[2]['amount'] for x in ctx.get('line_dr_ids')]) -
                       sum([x[2]['amount'] for x in ctx.get('line_cr_ids')]))
        return income

    @api.multi
    @api.depends('voucher_id.state')
    def _compute_posted(self):
        for rec in self:
            rec.posted = rec.voucher_id.state == 'posted' and True or False

    @api.multi
    @api.depends('date')
    def _compute_calendar_year(self):
        for rec in self:
            rec.calendar_year = rec.date and rec.date[:4] or False

    @api.model
    def _calculate_pit_amount_wht(self, date,
                                  partner_id, amount_income):
        if not amount_income or not partner_id:
            return 0.0
        AccountPIT = self.env['account.pit']
        PIT = self.env['personal.income.tax']
        calendar_year = date[:4]
        pit_lines = PIT.search([('partner_id', '=', partner_id),
                                ('calendar_year', '=', calendar_year),
                                ('posted', '=', True)])
        prev_income = sum([x.amount_income for x in pit_lines])
        prev_wht = - sum([x.amount_wht for x in pit_lines])
        income = prev_income + amount_income
        account_pits = AccountPIT.search(
            [('date_effective', '<=', date)], order='date_effective desc')
        account_pit = account_pits and account_pits[0] or False
        if not account_pit:
            raise ValidationError(
                _('No PIT Rate Table found for '
                  'calendar year %s') % (calendar_year,))
        rate_ranges = account_pit.rate_ids.filtered(
            lambda r: income > r.income_from and income <= r.income_to)
        if len(rate_ranges) != 1:
            raise ValidationError(_('No valid PIT Rate Range found'))
        rec = rate_ranges[0]
        expected_wht = (rec.amount_tax_max_accum - rec.amount_tax_max) + \
            (income - rec.income_from) * rec.tax_rate / 100
        return - (expected_wht - prev_wht)

    @api.onchange('amount_income', 'partner_id')
    def _onchange_partner_income(self):
        ctx = self._context.copy()
        voucher_date = self.voucher_id.date or ctx.get('voucher_date')
        self.amount_wht = self._calculate_pit_amount_wht(voucher_date,
                                                         self.partner_id.id,
                                                         self.amount_income,)


class AccountPIT(models.Model):
    _name = 'account.pit'
    _descripition = 'PIT Table'
    _rec_name = 'calendar_year'

    calendar_year = fields.Char(
        string='Calendar Year',
        size=4,
        required=True,
        default=lambda self: str(datetime.datetime.now().year),
    )
    date_effective = fields.Date(
        string='Effective Date',
        compute='_compute_date_effective',
        store=True,
        readonly=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    rate_ids = fields.One2many(
        'account.pit.rate',
        'pit_id',
        string='Withholding Tax Rates',
    )
    _sql_constraints = [
        ('year_uniq', 'unique (calendar_year)', 'The year must be unique !'),
    ]

    @api.one
    @api.depends('calendar_year')
    def _compute_date_effective(self):
        self.date_effective = '%s-01-01' % (self.calendar_year,)

    @api.one
    @api.constrains('rate_ids')
    def _check_rate_ids(self):
        i = 0
        prev_income_to = 0.0
        accum_tax = 0.0
        for rate in self.rate_ids:
            if i == 0 and rate.income_from != 0.0:
                raise UserError(_('Income amount must start from 0.0'))
            if i > 0 and \
                    float_compare(rate.income_from, prev_income_to, 2) != 0:
                raise UserError(
                    _('Discontinued income range!\n'
                      'Please make sure Income From = Previous Income To'))
            prev_income_to = rate.income_to
            accum_tax += rate.amount_tax_max
            rate.amount_tax_max_accum = accum_tax
            i += 1
        return


class AccountPITRate(models.Model):
    _name = 'account.pit.rate'
    _description = 'PIT Rates'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=100,
    )
    pit_id = fields.Many2one(
        'account.pit',
        string='PIT Table',
        ondelete='cascade',
        index=True,
    )
    income_from = fields.Float(
        string='Income From (>)',
    )
    income_to = fields.Float(
        string='Income To (<=)',
    )
    tax_rate = fields.Float(
        string='Tax Rate (%)',
    )
    amount_tax_max = fields.Float(
        string='Maximum Tax in Range',
        compute='_compute_amount_tax_max',
        store=True,
    )
    amount_tax_max_accum = fields.Float(
        string='Maximum Tax Accum',
        readonly=True,
    )

    @api.multi
    @api.depends('income_from', 'income_to', 'tax_rate')
    def _compute_amount_tax_max(self):
        for rec in self:
            rec.amount_tax_max = ((rec.income_to - rec.income_from) *
                                  (rec.tax_rate / 100))
