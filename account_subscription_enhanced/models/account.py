# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
import time


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
    model_type_id = fields.Many2one(
        'account.model.type',
        related='model_id.model_type_id',
        string='Model Type',
        store=True,
        readonly=True,
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
        # Filtered by Model type, when selected
        model_type_ids = self._context.get('model_type_ids', False)
        sublines = self
        if model_type_ids:
            sublines = sublines.filtered(
                lambda l: l.subscription_id.model_type_id.id in model_type_ids)
        # If no model types specified, generate for all.
        lines_normal = sublines.filtered(lambda l: not l.amount)
        lines_with_amount = sublines.filtered(lambda l: l.amount)
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

    model_type_id = fields.Many2one(
        'account.model.type',
        string='Type',
        ondelete='restrict',
    )
    lines_id = fields.One2many(
        copy=False,
    )

    @api.multi
    def generate(self, data=None):
        # Extra check for type amount manual
        if self._context.get('subline_amount', False):
            self.ensure_one()
            if len(self.lines_id) != 2:
                raise ValidationError(
                    _('Model template must have only 2 item lines!'))
        # --

        """ Overwrite for performance on create with (0,0,{...})"""

        if data is None:
            data = {}
        move_ids = []
        entry = {}
        AccountMove = self.env['account.move']
        PayTerm = self.env['account.payment.term']
        Period = self.env['account.period']
        context = self._context.copy()
        if data.get('date', False):
            context.update({'date': data['date']})

        move_date = context.get('date', time.strftime('%Y-%m-%d'))
        move_date = datetime.strptime(move_date, '%Y-%m-%d')
        for model in self:
            ctx = context.copy()
            ctx.update({'company_id': model.company_id.id})
            date = context.get('date', False)
            period = Period.with_context(ctx).find(date)
            ctx.update({
                'journal_id': model.journal_id.id,
                'period_id': period.id
            })
            try:
                entry['name'] = model.name % {
                    'year': move_date.strftime('%Y'),
                    'month': move_date.strftime('%m'),
                    'date': move_date.strftime('%Y-%m')}
            except:
                raise except_orm(
                    _('Wrong Model!'),
                    _('You have a wrong expression "%(...)s" in your model!'))
            move = AccountMove.create({
                'ref': entry['name'],
                'period_id': period.id,
                'journal_id': model.journal_id.id,
                'date': context.get('date', fields.Date.context_today(self))
            })
            move_ids.append(move.id)
            move_lines = []
            for line in model.lines_id:
                analytic_account_id = False
                if line.analytic_account_id:
                    if not model.journal_id.analytic_journal_id:
                        raise except_orm(
                            _('No Analytic Journal!'),
                            _("You have to define an analytic journal on the "
                              "'%s' journal!") % (model.journal_id.name,))
                    analytic_account_id = line.analytic_account_id.id
                val = {
                    'journal_id': model.journal_id.id,
                    'period_id': period.id,
                    'analytic_account_id': analytic_account_id
                }
                date_maturity = context.get('date', time.strftime('%Y-%m-%d'))
                if line.date_maturity == 'partner':
                    if not line.partner_id:
                        raise except_orm(
                            _('Error!'),
                            _("Maturity date of entry line generated by model "
                              "line '%s' of model '%s' is based on partner "
                              "payment term!\nPlease define partner on it!") %
                             (line.name, model.name))
                    payment_term_id = False
                    if (model.journal_id.type in
                        ('purchase', 'purchase_refund')) and \
                            line.partner_id.property_supplier_payment_term:
                        payment_term_id = \
                            line.partner_id.property_supplier_payment_term.id
                    elif line.partner_id.property_payment_term:
                        payment_term_id =\
                            line.partner_id.property_payment_term.id
                    if payment_term_id:
                        pterm_list = PayTerm.compute(payment_term_id, value=1,
                                                     date_ref=date_maturity)
                        if pterm_list:
                            pterm_list = [l[0] for l in pterm_list]
                            pterm_list.sort()
                            date_maturity = pterm_list[-1]
                val.update({
                    'name': line.name,
                    'quantity': line.quantity,
                    'debit': line.debit,
                    'credit': line.credit,
                    'account_id': line.account_id.id,
                    'partner_id': line.partner_id.id,
                    'date': context.get('date',
                                        fields.Date.context_today(self)),
                    'date_maturity': date_maturity
                })
                move_lines.append((0, 0, val))
            move.write({'line_id': move_lines})
        return move_ids


class AccountModelType(models.Model):
    _name = 'account.model.type'

    name = fields.Char(
        string='Name',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Model type name must be unique!'),
    ]


class AccountMove(models.Model):
    _inherit = 'account.move'

    model_id = fields.Many2one(
        'account.model',
        string='Template Model',
        ondelete='set null',
    )

    @api.model
    def _prepare_copy_fields(self, source_model, target_model):
        src_fields = [f for f, _x in source_model._fields.iteritems()]
        no_fields = [
            'id', '__last_update',
            'write_date', 'create_date', 'create_uid', 'write_uid',
        ]
        trg_fields = [f for f, _x in target_model._fields.iteritems()]
        return list((set(src_fields) & set(trg_fields)) - set(no_fields))

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.state != 'draft':
            raise ValidationError(_('Template can be used only on draft!'))
        self.line_id = False
        self.line_id = []
        ModelLine = self.env['account.model.line']
        MoveLine = self.env['account.move.line']
        line_fields = self._prepare_copy_fields(ModelLine, MoveLine)
        for line in self.model_id.lines_id:
            move_line = MoveLine.new()
            for field in line_fields:
                move_line[field] = line[field]
            self.line_id += move_line
