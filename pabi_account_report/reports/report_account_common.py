# -*- coding: utf-8 -*
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import time


class ReportAccountCommon(models.AbstractModel):
    _name = 'report.account.common'
    _inherit = 'xlsx.report'

    chart_account_id = fields.Many2one(
        'account.account',
        string='Chart of Accounts',
        domain=[('parent_id', '=', False)],
        required=True,
        default=lambda self: self._get_account(),
        help='Select Chart of Accounts',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    fiscalyear_start_id = fields.Many2one(
        'account.fiscalyear',
        string='Start Fiscal Year',
        default=lambda self: self._get_fiscalyear(),
    )
    fiscalyear_end_id = fields.Many2one(
        'account.fiscalyear',
        string='End Fiscal Year',
        default=lambda self: self._get_fiscalyear(),
    )
    fiscalyear_date_start = fields.Date(
        string='Start Fiscal Year Date',
        compute='_compute_fiscalyear_date',
    )
    fiscalyear_date_end = fields.Date(
        string='End Fiscal Year Date',
        compute='_compute_fiscalyear_date',
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_date', 'Dates'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_no',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    period_start_id = fields.Many2one(
        'account.period',
        string='Start Period',
    )
    period_end_id = fields.Many2one(
        'account.period',
        string='End Period',
    )

    @api.model
    def _get_account(self):
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('parent_id', '=', False)]
        account = self.env['account.account'].search(domain, limit=1)
        return account

    @api.model
    def _get_fiscalyear(self):
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', self.env.user.company_id.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        return fiscalyear

    @api.multi
    @api.depends('fiscalyear_start_id', 'fiscalyear_end_id')
    def _compute_fiscalyear_date(self):
        self.ensure_one()
        Fiscalyear = self.env['account.fiscalyear']
        date_start = self.fiscalyear_start_id.date_start
        date_stop = self.fiscalyear_end_id.date_stop
        if date_start or date_stop:
            if not date_start:
                fiscalyear = Fiscalyear.search([], order="date_start", limit=1)
                date_start = fiscalyear.date_start
            if not date_stop:
                fiscalyear = Fiscalyear.search(
                    [], order="date_stop desc", limit=1)
                date_stop = fiscalyear.date_stop
        self.fiscalyear_date_start = date_start
        self.fiscalyear_date_end = date_stop

    @api.onchange('chart_account_id')
    def _onchange_chart_account_id(self):
        chart_account_id = self.chart_account_id
        if chart_account_id:
            company = chart_account_id.company_id
            now = time.strftime('%Y-%m-%d')
            domain = [('company_id', '=', company.id),
                      ('date_start', '<=', now),
                      ('date_stop', '>=', now)]
            fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
            self.company_id = company
            self.fiscalyear_start_id = fiscalyear
            self.fiscalyear_end_id = fiscalyear

    @api.multi
    def run_report(self):
        raise ValidationError(_('Not implemented.'))
