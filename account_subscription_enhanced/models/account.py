# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountSubscription(models.Model):
    _inherit = 'account.subscription'

    consider_month_end = fields.Boolean(
        string='Consider Month End',
        default=False,
    )
    type = fields.Selection(
        [('standard', 'Standard'),
         ('amount', 'Amount (manual)'),
         ],
        string='Type',
        default='standard',
        required=True,
    )
    amount = fields.Float(
        string='Amount',
    )
    rate_type = fields.Selection(
        [('daily', 'Daily'),
         ('monthly', 'Monthly'),
         ('yearly', 'Yearly'),
         ],
        string='Rate',
    )
    rate = fields.Float(
        string='Rate',
        compute='_compute_rate',
    )
    rate_err_message = fields.Char(
        string='Error Message',
    )

    @api.multi
    @api.depends('amount', 'rate_type')
    def _compute_rate(self):
        for rec in self:
            rec.rate_err_message = False
            if not rec.lines_id:
                continue
            date_min = min(rec.lines_id.mapped('date'))
            date_max = max(rec.lines_id.mapped('date_end'))
            if not date_min or not date_max:
                rec.rate = 0.0
                continue
            date_start = datetime.strptime(date_min, '%Y-%m-%d')
            date_end = datetime.strptime(date_max, '%Y-%m-%d') + \
                relativedelta(days=1)
            days = (date_end - date_start).days
            r = relativedelta(date_end, date_start)
            if rec.rate_type == 'daily':
                rec.rate = rec.amount / days
            elif rec.rate_type == 'monthly':
                if r.days:
                    rec.rate_err_message = \
                        _('Cannot calculate monthly rate, days residual!')
                    rec.rate = 0.0
                    continue
                rec.rate = rec.amount / (r.years * 12 + r.months)
            elif rec.rate_type == 'yearly':
                if r.days or r.months:
                    rec.rate_err_message = \
                        _('Cannot calculate yearly rate, '
                          'months/days residual!')
                    rec.rate = 0.0
                    continue
                rec.rate = rec.amount / r.years
        return

    @api.onchange('period_type')
    def _onchange_period_type(self):
        self.consider_month_end = False

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
        """ Overwrite """
        for sub in self:
            ds = sub.date_start
            date = datetime.strptime(ds, '%Y-%m-%d')
            date_last = self._get_date_last(sub)
            i = 0
            while i < sub.period_total:
                line = self.env['account.subscription.line'].create({
                    'date': date.strftime('%Y-%m-%d'),
                    'subscription_id': sub.id,
                })
                # Consider month end
                if self.consider_month_end:
                    if date.day != 1:
                        date = datetime.strptime(
                            date.strftime('%Y-%m-01'), '%Y-%m-%d')
                        i -= 1
                # --
                if sub.period_type == 'day':
                    date = date + relativedelta(days=sub.period_nbr)
                if sub.period_type == 'month':
                    date = date + relativedelta(months=sub.period_nbr)
                if sub.period_type == 'year':
                    date = date + relativedelta(years=sub.period_nbr)
                i += 1
                if i == sub.period_total:
                    line.date_end = date_last - relativedelta(days=1)
                else:
                    line.date_end = date - relativedelta(days=1)
        self.write({'state': 'running'})
        return True

    @api.multi
    def calculate_amount(self):
        for rec in self:
            if not rec.rate_type or not rec.rate:
                continue
            num_line = len(rec.lines_id)
            sum_amount = 0.0
            i = 0
            while i < num_line:
                line = rec.lines_id[i]
                date_start = datetime.strptime(line.date, '%Y-%m-%d')
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
                    line.amount = (rec.amount - sum_amount) + line.amount
        return


class AccountSubscriptionLine(models.Model):
    _inherit = 'account.subscription.line'

    type = fields.Selection(
        [('standard', 'Standard'),
         ('amount', 'Amount (manual)'),
         ],
        string='Type',
        related='subscription_id.type',
    )
    date_end = fields.Date(
        string='To Date',
    )
    amount = fields.Float(
        string='Amount',
    )

    @api.multi
    def move_create(self):
        move_ids = []
        lines_normal = self.filtered(lambda l: not l.amount)
        lines_with_amount = self.filtered(lambda l: l.amount)
        # Normal case
        _ids = super(AccountSubscriptionLine, lines_normal).move_create()
        move_ids.extend(_ids)
        # Amount case
        for line in lines_with_amount:
            subline = line.with_context(subline_amount=line.amount)
            _ids = super(AccountSubscriptionLine, subline).move_create()
            move_ids.extend(_ids)
        return move_ids


class AccountModel(models.Model):
    _inherit = 'account.model'

    @api.multi
    def generate(self, data=None):
        if self._context.get('subline_amount', False):
            self.ensure_one()
            if len(self.lines_id) != 2:
                raise ValidationError(
                    _('Model template must have only 2 item lines!'))
        return super(AccountModel, self).generate(data=data)
