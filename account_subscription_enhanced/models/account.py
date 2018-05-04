# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
from openerp.tools.safe_eval import safe_eval as eval

import dateutil
import openerp
from openerp import workflow


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
    forced_done = fields.Boolean(
        string='Is forced done?',
        boolean=False,
        help="Checked, if Forced Done. It will allow to reset back to running."
    )

    @api.multi
    def force_done(self):
        self.write({'state': 'done',
                    'force_done': True})

    @api.multi
    def back_to_running(self):
        self.write({'state': 'running',
                    'force_done': False})

    @api.multi
    @api.depends('amount', 'rate_type')
    def _compute_rate(self):
        for rec in self:
            rec.rate_err_message = False
            if not rec.lines_id:
                continue
            date_min = min(rec.lines_id.mapped('date_start'))
            date_max = max(rec.lines_id.mapped('date'))
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
            date_start = datetime.strptime(ds, '%Y-%m-%d')
            date_last = self._get_date_last(sub)
            i = 0
            sublines = []
            while i < sub.period_total:
                line = {
                    'date_start': date_start.strftime('%Y-%m-%d'),
                    'subscription_id': sub.id,
                }
                # Consider month end
                if self.consider_month_end:
                    if date_start.day != 1:
                        date_start = datetime.strptime(
                            date_start.strftime('%Y-%m-01'), '%Y-%m-%d')
                        i -= 1
                # --
                if sub.period_type == 'day':
                    date_start = \
                        date_start + relativedelta(days=sub.period_nbr)
                if sub.period_type == 'month':
                    date_start = \
                        date_start + relativedelta(months=sub.period_nbr)
                if sub.period_type == 'year':
                    date_start = \
                        date_start + relativedelta(years=sub.period_nbr)
                i += 1
                if i == sub.period_total:
                    line['date'] = date_last - relativedelta(days=1)
                else:
                    line['date'] = date_start - relativedelta(days=1)
                sublines.append((0, 0, line))
            sub.write({'lines_id': sublines})
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
                date_start = datetime.strptime(line.date_start, '%Y-%m-%d')
                date_end = datetime.strptime(line.date, '%Y-%m-%d') + \
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

    @api.multi
    def open_entries(self):
        self.ensure_one()
        action = False
        code = self.model_id.journal_id.code
        if code == 'AJN':
            action = self.env.ref('pabi_account_move_adjustment.'
                                  'action_journal_adjust_no_budget')
        elif code == 'AJB':
            action = self.env.ref('pabi_account_move_adjustment.'
                                  'action_journal_adjust_budget')
        if not action:
            raise ValidationError(_('Invalid journal code from model!'))
        result = action.read()[0]
        move_ids = self.lines_id.mapped('move_id').ids
        result.update({'domain': [('id', 'in', move_ids)]})
        return result


class AccountSubscriptionLine(models.Model):
    _inherit = 'account.subscription.line'

    type = fields.Selection(
        [('standard', 'Standard'),
         ('amount', 'Amount (manual)'),
         ],
        string='Type',
        related='subscription_id.type',
    )
    date_start = fields.Date(
        string='From Date',
        required=True,
    )
    date = fields.Date(  # change label
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
        context = self._context.copy()
        subscriptions = self.mapped('subscription_id')
        for subscription in subscriptions:
            context.update({'subscription_id': subscription.id,
                            'subline_amount': False})
            # Subline for this subscription
            sublines = self.filtered(lambda l:
                                     l.subscription_id == subscription)
            if model_type_ids:
                sublines = sublines.filtered(
                    lambda l: l.subscription_id.model_type_id.id in
                    model_type_ids)
            # If no model types specified, generate for all.
            lines_normal = sublines.filtered(lambda l: not l.amount)
            lines_with_amount = sublines.filtered(lambda l: l.amount)
            # Normal case
            _ids = super(AccountSubscriptionLine,
                         lines_normal.with_context(context)).move_create()
            move_ids.extend(_ids)
            # Amount case
            for line in lines_with_amount:
                context.update({'subline_amount': line.amount})
                _ids = super(AccountSubscriptionLine,
                             line.with_context(context)).move_create()
                move_ids.extend(_ids)
        return move_ids


class AccountModel(models.Model):
    _inherit = 'account.model'

    model_type_id = fields.Many2one(
        'account.model.type',
        string='Type',
        ondelete='restrict',
        required=True,
    )
    to_be_reversed = fields.Boolean(
        string='To Be Reversed',
        default=False,
        help="Journal Entry created by this model will also be reversed",
    )
    reverse_type = fields.Selection(
        [('manual', 'Manual (by user)'),
         ('auto', 'Auto (1st day, following month)')],
        string='Reverse Type',
        required=True,
        default='manual',
        help="* Manual: Journal Entry created will be marked for Reversal but "
        "user will have to do it manually.\n"
        "* Auto: As soon as Recurring Entry is created, the reveral will be "
        "auto created, and use 1st date of follwing month as entry date.",
    )
    legend = fields.Text(
        default=lambda self:
        _('You can specify year, month and date in the name of the model '
          'using the following labels:\n\n%(year)s: To Specify Year \n'
          '%(month)s: To Specify Month \n%(date)s: Current Date\n\ne.g. '
          'My model on %(date)s\n\n'
          'Additionally, if the model line is called from '
          'Define Recurring Entries (account.subscription),\nyou can use '
          'python code to get the dynamic values from the Define Recurring '
          'into the model line using ${object} (account.subscription),\n'
          'e.g. ${object.name} will get the name of Define Recurring\n')
    )

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default['name'] = _('%s (copy)') % self.name
        return super(AccountModel, self).copy(default)

    @api.onchange('model_type_id')
    def _onchange_model_type_id(self):
        self.journal_id = self.model_type_id.journal_id
        self.to_be_reversed = self.model_type_id.to_be_reversed
        self.reverse_type = self.model_type_id.reverse_type

    @api.multi
    def generate(self, data=None):
        if data is None:
            data = {}
        # Extra check for type amount manual
        if self._context.get('subline_amount', False):
            self.ensure_one()
            if len(self.lines_id) != 2:
                raise ValidationError(
                    _('Model "%s" is using manual amount and must have '
                      'only 2 entry lines!' % self.name))
        move_ids = self._generate(data)
        return move_ids

    @api.multi
    def _generate(self, data=None):
        """ Overwrite super's generate(), performance on create (0,0,{...}) """
        if data is None:
            data = {}
        move_ids = []
        context = self._context.copy()
        if data.get('date', False):
            context.update({'date': data['date']})
        for model in self:
            move = self.with_context(context)._create_move(model)
            move_ids.append(move.id)
            # Reversal if auto
            if model.to_be_reversed and model.reverse_type == 'auto':
                if context.get('end_period_date', False):
                    context.update({'date': context.get('end_period_date')})
                date = context.get('date', False)
                date = (datetime.strptime(date, '%Y-%m-%d') +
                        relativedelta(days=1)).strftime('%Y-%m-%d')
                reversed_move_ids = move.create_reversals(date)
                move_ids += reversed_move_ids
        return move_ids

    @api.model
    def _create_move(self, model):
        AccountMove = self.env['account.move']
        move_dict = self._prepare_move(model)
        move_lines = self._prepare_move_line(model)
        move_dict['line_id'] = move_lines
        move = AccountMove.create(move_dict)
        return move

    @api.model
    def _prepare_move(self, model):
        Period = self.env['account.period']
        context = self._context.copy()
        # kittiu:Change date of JE, if end_period_date is passed from wizard
        if context.get('end_period_date', False):
            context.update({'date': context.get('end_period_date')})
        # --
        date = context.get('date', False)
        ctx = context.copy()
        period = Period.with_context(ctx).find(date)
        ctx.update({
            'company_id': model.company_id.id,
            'journal_id': model.journal_id.id,
            'period_id': period.id
        })
        move_date = context.get('date', time.strftime('%Y-%m-%d'))
        move_date = datetime.strptime(move_date, '%Y-%m-%d')
        entry = {}
        try:
            entry['name'] = model.name % {
                'year': move_date.strftime('%Y'),
                'month': move_date.strftime('%m'),
                'date': move_date.strftime('%Y-%m')}
        except:
            raise except_orm(
                _('Wrong Model!'),
                _('You have a wrong expression "%(...)s" in your model!'))
        move_dict = {
            'ref': entry['name'],
            'period_id': period.id,
            'journal_id': model.journal_id.id,
            'date': context.get('date', fields.Date.context_today(self)),
            # extra
            'to_be_reversed': model.to_be_reversed,
        }
        return move_dict

    @api.model
    def _get_eval_context(self, active_model, active_id):
        """ Prepare the context used when evaluating python code, like the
        condition or code server actions.

        :returns: dict -- evaluation context given to (safe_)eval """
        env = openerp.api.Environment(self._cr, self._uid, self._context)
        model = env[str(active_model)]
        obj = model.browse(active_id)
        eval_context = {
            # python libs
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            # orm
            'env': env,
            'model': model,
            'workflow': workflow,
            # Exceptions
            'ValidationError': openerp.exceptions.ValidationError,
            # record
            # deprecated and define record (active_id) and records (active_ids)
            'object': obj,
            'obj': obj,
            # Deprecated use env or model instead
            'self': obj,
            'pool': self.pool,
            'cr': self._cr,
            'uid': self._uid,
            'context': self._context,
            'user': env.user,
        }
        return eval_context

    @api.model
    def _prepare_move_line(self, model):
        PayTerm = self.env['account.payment.term']
        Period = self.env['account.period']
        Subscription = self.env['account.subscription']
        move_lines = []
        context = self._context.copy()
        date = context.get('date', False)
        ctx = context.copy()
        period = Period.with_context(ctx).find(date)
        ctx.update({
            'company_id': model.company_id.id,
            'journal_id': model.journal_id.id,
            'period_id': period.id
        })
        eval_context = False
        if ctx.get('subscription_id', False):
            eval_context = self._get_eval_context(Subscription._model,
                                                  ctx['subscription_id'])
        for line in model.lines_id:
            name = line.name
            if '${' in name and eval_context:
                field_code = (line.name.split('${'))[1].split('}')[0]
                field_code = 'value=' + field_code
                try:
                    eval(field_code, eval_context, mode="exec", nocopy=True)
                    name = eval_context.get('value', False)
                except Exception:
                    raise ValidationError(
                        _("Wrong code (%s) defined in line\
                        in Recurring Models: %s") % (name, model.name))
            if '${' in name and not eval_context:
                raise ValidationError(
                    _("Sorry!, You can not use %s while creating entries "
                      "from Model form!") % (name,))
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
                'name': name,
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
        return move_lines


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
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
    )
    to_be_reversed = fields.Boolean(
        string='To Be Reversed',
        default=False,
        help="Journal Entry created by this model will also be reversed",
    )
    reverse_type = fields.Selection(
        [('manual', 'Manual (by user)'),
         ('auto', 'Auto (1st day, following month)')],
        string='Reverse Type',
        required=True,
        default='manual',
        help="* Manual: Journal Entry created will be marked for Reversal but "
        "user will have to do it manually.\n"
        "* Auto: As soon as Recurring Entry is created, the reveral will be "
        "auto created, and use 1st date of follwing month as entry date.",
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
