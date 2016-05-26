# -*- coding: utf-8 -*-

from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class BudgetReleaseWizard(models.TransientModel):
    _name = "budget.release.wizard"

    release_ids = fields.One2many(
        'budget.release.line',
        'wizard_id',
        string='Release Lines',
    )

    @api.model
    def default_get(self, fields):
        res = super(BudgetReleaseWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        plan = self.env['account.budget.line'].browse(active_id)
        releases = []
        interval = 3
        start_period = 1
        next_period = start_period
        months = 12
        # i.e., [[3,4,5], [6,7,8], [9,10,11], [12]]
        periods = []
        sub_period = []
        for i in range(months):
            mo = i+1
            if mo < start_period:
                continue
            if mo == next_period:
                next_period += interval
                print next_period
                if sub_period:
                    periods.append(sub_period)
                    sub_period = []
            sub_period.append(mo)
        periods.append(sub_period)
        # --
        for period in periods:
            from_period = period[0]
            to_period = period[-1]
            release = plan['r'+str(to_period)]
            planned_amount = 0.0
            released_amount = 0.0
            for i in period:
                planned_amount += plan['m'+str(i)]
                released_amount += plan['r'+str(i)] and plan['m'+str(i)] or 0.0
            line = {'from_period': from_period,
                    'to_period': to_period,
                    'planned_amount': planned_amount,
                    'released_amount': released_amount,
                    'release': release,
                    'active': True,
                    }
            releases.append((0, 0, line))
        res['release_ids'] = releases
        return res

    @api.multi
    def do_release(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        budget_line = self.env['account.budget.line'].browse(active_id)
        releases = {}
        for r in self.release_ids:
            for i in range(r.from_period, r.to_period + 1):
                releases.update({'r'+str(i): r.release})
        return budget_line.release_budget_line(releases)


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
