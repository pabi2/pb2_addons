# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta


class BudgetReleaseWizard(models.TransientModel):
    _name = "budget.release.wizard"

    release_ids = fields.One2many(
        'budget.release.line',
        'wizard_id',
        string='Release Lines',
    )
    progress = fields.Float(
        string='Progress',
    )
    amount_to_release = fields.Float(
        string="Amount To Release",
    )

    @api.onchange('amount_to_release')
    def _compute_progress(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        BudgetLine = self.env['account.budget.line']
        budget_lines = False
        if active_model == 'account.budget.line':
            budget_lines = BudgetLine.search([('id', '=', active_id)])
        elif active_model == 'account.budget':
            budget_lines = BudgetLine.search([('budget_id', '=', active_id)])

        planned_amount = sum([l.planned_amount for l in budget_lines])
        released_amount = sum([l.released_amount for l in budget_lines])

        if not planned_amount:
            self.progress = 0.0
        else:
            self.progress = released_amount / planned_amount * 100

    # TODO: Should move to budget plan object?
    @api.model
    def _domain_release_pattern(self, plan):
        return [('fiscal_id', '=', plan.fiscalyear_id.id)]

    @api.model
    def _get_release_pattern(self, plan):
        domain = self._domain_release_pattern(plan)
        budget_level = \
            self.env['account.fiscalyear.budget.level'].search(domain, limit=1)
        interval = budget_level.release_interval and \
            int(budget_level.release_interval) or 1
        interval = False #probuse
        start_period = 1  # by default
        is_auto_release = budget_level.is_auto_release
        return interval, start_period, is_auto_release

    @api.model
    def _calc_release_periods(self, interval, start_period):
        # i.e., if interval = 3 and start_period = 3
        # return [[3,4,5], [6,7,8], [9,10,11], [12]]
        periods = []
        sub_period = []
        next_period = start_period
        for i in range(12):  # Max 12 months
            mo = i+1
            if mo < start_period:
                continue
            if mo == next_period:
                next_period += interval
                if sub_period:
                    periods.append(sub_period)
                    sub_period = []
            sub_period.append(mo)
        if sub_period:
            periods.append(sub_period)
        return periods

    @api.model
    def _prepare_budget_release_wizard(self, plan):
        budget_lines = False
        if plan._name == 'account.budget.line':
            budget_lines = BudgetLine.search([('id', '=', plan.id)])
        elif plan._name == 'account.budget':
            budget_lines = BudgetLine.search([('budget_id', '=', plan)])
        else:
            raise UserError(_('Not a budgeting model'))

        BudgetLine = self.env['account.budget.line']
        release_result = {}
        for line in budget_lines:
            if active_model == 'account.budget.line':
                release_result.update({line.id : self.amount_to_release})
            else:
                release_result.update(
                    {line.id: line.planned_amount - line.released_amount})
        return release_result

    @api.model
    def _prepare_budget_release_table(self, res_model, res_id):
        plan = False
        if res_model == 'account.budget.line':
            plan = self.env['account.budget.line'].browse(res_id)
        elif res_model == 'account.budget':
            plan = self.env['account.budget'].browse(res_id)
        else:
            raise UserError(_('Not a budgeting model'))
        interval, start_period, _dummy = self._get_release_pattern(plan)
        periods = self._calc_release_periods(interval, start_period)
        releases = self._prepare_budget_release_wizard(periods, plan)
        return releases

    @api.model
    def default_get(self, fields):
        res = super(BudgetReleaseWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        record = self.env[active_model].browse(active_id)

        BudgetLine = self.env['account.budget.line']
        budget_lines = False
        if active_model == 'account.budget.line':
            budget_lines = BudgetLine.search([('id', '=', active_id)])
        elif active_model == 'account.budget':
            budget_lines = BudgetLine.search([('budget_id', '=', active_id)])

        planned_amount = sum([l.planned_amount for l in budget_lines])
        released_amount = sum([l.released_amount for l in budget_lines])
        res['amount_to_release'] = planned_amount - released_amount
        return res

    @api.multi
    def do_release(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        BudgetLine = self.env['account.budget.line']
        budget_lines = False
        if active_model == 'account.budget.line':
            budget_lines = BudgetLine.search([('id', '=', active_id)])
        elif active_model == 'account.budget':
            budget_lines = BudgetLine.search([('budget_id', '=', active_id)])

        release_result = {}
        for line in budget_lines:
            if active_model == 'account.budget.line':
                release_result.update({line.id : self.amount_to_release})
            else:
                release_result.update(
                    {line.id : line.planned_amount - line.released_amount})
        budget_lines.release_budget_line(release_result)


class BudgetReleaseLine(models.TransientModel):
    _name = "budget.release.line"

    wizard_id = fields.Many2one(
        'budget.release.wizard',
        string='Wizard',
        readonly=True,
    )
    from_period = fields.Integer(
        string='From Period',
        readonly=True,
    )
    to_period = fields.Integer(
        string='To Period',
        readonly=True,
    )
    from_date = fields.Date(
        string='From Date',
        readonly=True,
    )
    to_date = fields.Date(
        string='To Date',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        digits_compute=dp.get_precision('Account'),
        readonly=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        digits_compute=dp.get_precision('Account'),
        readonly=True,
    )
    release = fields.Boolean(
        string='Release',
        default=False,
    )
    ready = fields.Boolean(
        string='Ready to release',
        help="Whether budget should be released according to release interval",
    )
    past = fields.Boolean(
        string='Past release',
        help="Whether this is past release, and can't be unreleased",
    )

    @api.onchange('release')
    def _onchange_release(self):
        self.released_amount = self.release and self.planned_amount or 0.0
