# -*- coding: utf-8 -*-
import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare
from openerp.addons.l10n_th_account.models.account_voucher \
    import WHT_CERT_INCOME_TYPE


class PersonalIncomeTax(models.Model):
    _name = 'personal.income.tax'
    _description = 'Personal Income Tax'
    _order = 'calendar_year, sequence, id'

    sequence = fields.Char(
        string='Sequence',
        readonly=True,
        size=500,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Payment',
        index=True,
        ondelete='cascade',
        # required=True,
        domain=[('state', 'not in', ['draft', 'cancel'])],
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        index=True,
        ondelete='cascade',
        # required=True,
        domain=[('state', 'not in', ['draft', 'cancel'])],
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)],
        index=True,
        required=True,
        ondelete='cascade',
    )
    posted = fields.Boolean(
        string='Posted',
        readonly=True,
        help="Once posted, sequence will run and WHT will be calculated"
    )
    manual = fields.Boolean(
        string='Manual',
        default=False,
        help="Manually add line in Supplier window",
    )
    date = fields.Date(
        string='Date',
        # related='voucher_id.date',
        compute='_compute_date',
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
    precalc_wht = fields.Float(
        string='Precalc WHT Amount',
        help="This field show amount of WHT if posted now!"
    )
    amount_wht = fields.Float(
        string='WHT Amount',
        compute='_compute_amount_wht',
        store=True,
        help="This field show the real WHT amount, as posted."
    )
    wht_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
        size=500,
    )

    # _sql_constraints = [
    #     ('pit_uniq', 'unique (voucher_id, partner_id)',
    #      'Duplicated supplier on PIT!'),
    # ]

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
            income += \
                (sum([x[2]['amount'] for x in ctx.get('line_dr_ids', [])]) -
                 sum([x[2]['amount'] for x in ctx.get('line_cr_ids', [])]))
        return income

    @api.multi
    @api.depends('voucher_id', 'invoice_id')
    def _compute_date(self):
        for rec in self:
            rec.date = rec.voucher_id and rec.voucher_id.date or \
                rec.invoice_id.date_invoice

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
        PITYearly = self.env['personal.income.tax.yearly']
        calendar_year = date[:4]
        # Get current WTH state of this partner of this year
        current_pit = PITYearly.search([('partner_id', '=', partner_id),
                                        ('calendar_year', '=', calendar_year),
                                        ])
        total_income = current_pit.amount_income + amount_income
        # Calculate expected WHT for total income (on this year)
        expected_wht = AccountPIT.calculate_wht(date, total_income)
        return expected_wht - current_pit.amount_wht

    @api.multi
    @api.depends('posted')
    def _compute_amount_wht(self):
        for rec in self:
            if rec.posted:
                # kittiu: we now allow to change amount wht
                # otherwise, we should use _calculate_pit_amount_wht()
                amount_wht = rec.precalc_wht
                # amount_wht = self._calculate_pit_amount_wht(rec.date,
                #                                             rec.partner_id.id,
                #                                             rec.amount_income)
                rec.amount_wht = amount_wht

    @api.onchange('amount_income', 'partner_id', 'voucher_id', 'invoice_id')
    def _onchange_partner_income(self):
        ctx = self._context.copy()
        date = self.voucher_id.date or ctx.get('voucher_date')
        if self.invoice_id:
            date = self.invoice_id.date_invoice
        self.precalc_wht = self._calculate_pit_amount_wht(
            date, self.partner_id.id, self.amount_income)

    @api.onchange('voucher_id')
    def _onchange_voucher(self):
        if self.voucher_id:
            self.invoice_id = False

    @api.onchange('invoice_id')
    def _onchange_invoice(self):
        if self.invoice_id:
            self.voucher_id = False

    @api.multi
    def write(self, vals):
        res = super(PersonalIncomeTax, self).write(vals)
        for rec in self:
            self.env['personal.income.tax.yearly'].register(rec.calendar_year,
                                                            rec.partner_id.id)
        return res

    @api.multi
    def unlink(self):
        if len(self.filtered('posted')) > 0:
            raise ValidationError(_('Posted records can not be deleted!'))
        return super(PersonalIncomeTax, self).unlink()

    @api.multi
    def action_post(self):
        self.ensure_one()
        self.write({
            'posted': True,
            'sequence': self.env['ir.sequence'].next_by_code('pit.sequence')
        })
        if self.precalc_wht != self.amount_wht:
            raise ValidationError(_('Invalid PIT Withholding'))
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class PersonalIncomeTaxYearly(models.Model):
    _name = 'personal.income.tax.yearly'
    _description = 'Personal Income Tax by Year'

    partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        ondelete='cascade',
        readonly=True,
    )
    calendar_year = fields.Char(
        string='Calendar Year',
        readonly=True,
        size=4,
    )
    amount_income = fields.Float(
        string='Income',
        readonly=True,
    )
    amount_wht = fields.Float(
        string='Withholding Amount',
        readonly=True,
    )
    _sql_constraints = [
        ('pity_uniq', 'unique (partner_id, calendar_year)',
         'Duplicated supplier on PIT Yearly!'),
    ]

    @api.model
    def register(self, calendar_year, partner_id):
        income_tax_year = self.search([('calendar_year', '=', calendar_year),
                                       ('partner_id', '=', partner_id)])
        if not income_tax_year:
            income_tax_year = self.create({
                'partner_id': partner_id,
                'calendar_year': calendar_year,
            })
        income_tax_year.update_amount()
        return True

    @api.multi
    def update_amount(self):
        self.ensure_one()
        income_tax_lines = self.env['personal.income.tax'].search(
            [('calendar_year', '=', self.calendar_year),
             ('partner_id', '=', self.partner_id.id),
             ('posted', '=', True)])
        amount_income = sum([x.amount_income for x in income_tax_lines])
        amount_wht = sum([x.amount_wht for x in income_tax_lines])
        vals = {'amount_income': amount_income,
                'amount_wht': amount_wht}
        self.write(vals)
        return True


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
        copy=True,
    )

    @api.multi
    @api.depends('calendar_year')
    def _compute_date_effective(self):
        for rec in self:
            rec.date_effective = '%s-01-01' % (rec.calendar_year,)

    @api.multi
    @api.constrains('rate_ids')
    def _check_rate_ids(self):
        for rec in self:
            i = 0
            prev_income_to = 0.0
            accum_tax = 0.0
            for rate in rec.rate_ids:
                if i == 0 and rate.income_from != 0.0:
                    raise ValidationError(
                        _('Income amount must start from 0.0'))
                if i > 0 and float_compare(rate.income_from,
                                           prev_income_to, 2) != 0:
                    raise ValidationError(
                        _('Discontinued income range!\n'
                          'Please make sure Income From = Previous Income To'))
                prev_income_to = rate.income_to
                accum_tax += rate.amount_tax_max
                rate.amount_tax_max_accum = accum_tax
                i += 1
        return

    @api.model
    def calculate_wht(self, date, income):
        calendar_year = date[:4]
        account_pits = self.search(
            [('date_effective', '<=', date)], order='date_effective desc')
        account_pit = account_pits and account_pits[0] or False
        if not account_pit:
            raise ValidationError(
                _('No PIT Rate Table found for '
                  'calendar year %s') % (calendar_year,))
        sign = income < 0 and -1 or 1
        rate_ranges = account_pit.rate_ids.filtered(
            lambda r:
            abs(income) > r.income_from and
            abs(income) <= r.income_to)
        if len(rate_ranges) != 1:
            raise ValidationError(_('No valid PIT Rate Range found'))
        rec = rate_ranges[0]
        expected_wht = (rec.amount_tax_max_accum - rec.amount_tax_max) + \
            (abs(income) - rec.income_from) * rec.tax_rate / 100
        return sign * expected_wht


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
