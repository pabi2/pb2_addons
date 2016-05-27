# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp


class BudgetReleaseWizard(models.TransientModel):
    _name = "budget.release.wizard"

    release_ids = fields.One2many(
        'budget.release.line',
        'wizard_id',
        string='Release Lines',
    )

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
        start_period = 1  # by default
        return interval, start_period

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
    def _prepare_budget_release_wizard(self, periods, plan):
        if plan._name == 'account.budget.line':
            return plan._prepare_budget_line_release(periods)
        elif plan._name == 'account.budget':
            return plan._prepare_budget_release(periods)
        else:
            raise UserError(_('Not a budgeting model'))

    @api.model
    def default_get(self, fields):
        res = super(BudgetReleaseWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        plan = False
        if active_model == 'account.budget.line':
            plan = self.env['account.budget.line'].browse(active_id)
        elif active_model == 'account.budget':
            plan = self.env['account.budget'].browse(active_id)
        else:
            raise UserError(_('Not a budgeting model'))
        interval, start_period = self._get_release_pattern(plan)
        periods = self._calc_release_periods(interval, start_period)
        releases = self._prepare_budget_release_wizard(periods, plan)
        res['release_ids'] = [(0, 0, r) for r in releases]
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
        releases = {}
        for r in self.release_ids:
            for i in range(r.from_period, r.to_period + 1):
                releases.update({'r'+str(i): r.release})
        budget_lines.release_budget_line(releases)


class BudgetReleaseLine(models.TransientModel):
    _name = "budget.release.line"

    wizard_id = fields.Many2one(
        'budget.release.wizard',
        string='Wizard',
        readonly=True,
    )
    from_period = fields.Integer(
        string='From',
        readonly=True,
    )
    to_period = fields.Integer(
        string='To',
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

    @api.onchange('release')
    def _onchange_release(self):
        self.released_amount = self.release and self.planned_amount or 0.0
