# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountTrialBalanceWizard(models.TransientModel):
    _name = 'account.trial.balance.wizard'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        default=lambda self: self.env['account.fiscalyear'].find(),
        required=True,
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_date', 'Date'),
         ('filter_period', 'Periods')],
        string='Filter by',
        default='filter_no',
        required=True
    )
    period_start = fields.Many2one(
        'account.period',
        string='Start Period',
        domain="[('fiscalyear_id', '=', fiscalyear_id)]",
    )
    period_stop = fields.Many2one(
        'account.period',
        string='End Period',
        domain="[('fiscalyear_id', '=', fiscalyear_id)]",
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_stop = fields.Date(
        string='End Date',
    )
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        string='Target Moves',
        required=True,
        default='posted',
    )
    with_movement = fields.Boolean(
        string='With Movement',
        default=True,
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )

    @api.onchange('fiscalyear_id', 'filter')
    def _onchange_fiscalyear_id(self):
        self.date_start = self.fiscalyear_id.date_start
        self.date_stop = self.fiscalyear_id.date_stop
        self.period_start = self.env['account.period'].find(dt=self.date_start)
        self.period_stop = self.env['account.period'].find(dt=self.date_stop)

    @api.onchange('period_start')
    def _onchange_period_start(self):
        self.date_start = self.period_start.date_start

    @api.onchange('period_stop')
    def _onchange_period_stop(self):
        self.date_stop = self.period_stop.date_stop

    @api.multi
    def run_report(self):
        self.ensure_one()
        TB = self.env['account.trial.balance.report']
        report_id = TB.generate_report(self.fiscalyear_id.id,
                                       self.date_start,
                                       self.date_stop,
                                       self.target_move,
                                       self.with_movement,
                                       self.charge_type)
        action = self.env.ref('account_trial_balance_report.'
                              'action_account_trial_balance_report')
        result = action.read()[0]
        result.update({'res_id': report_id,
                       'domain': [('id', '=', report_id)]})
        return result
