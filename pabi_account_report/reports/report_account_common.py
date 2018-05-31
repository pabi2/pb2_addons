# -*- coding: utf-8 -*
import time
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class ReportAccountCommon(models.AbstractModel):
    _name = 'report.account.common'
    _inherit = 'xlsx.report'

    chart_account_id = fields.Many2one(
        'account.account',
        string='Chart of Account',
        help='Select Charts of Accounts',
        required=True,
        domain=[('parent_id', '=', False)],
        default=lambda self: self._get_account(),
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    fiscalyear_ids = fields.Many2many(
        'account.fiscalyear',
        'report_account_common_fiscalyear_rel',
        'report_id', 'fiscalyear_id',
        string='Fiscal Year(s)',
        default=lambda self: self._get_fiscalyear(),
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_date', 'Date'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_no',
    )
    date_from = fields.Date(
        string='Start Date',
    )
    date_to = fields.Date(
        string='End Date',
    )
    period_from = fields.Many2one(
        'account.period',
        string='Start Period',
    )
    period_to = fields.Many2one(
        'account.period',
        string='End Period',
    )

    @api.model
    def _get_account(self):
        domain = [('parent_id', '=', False),
                  ('company_id', '=', self.env.user.company_id.id)]
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
            self.fiscalyear_ids = fiscalyear

    @api.onchange('filter')
    def _onchange_filter(self):
        context = self._context.copy()
        filter = self.filter
        fiscalyear_ids = False
        if context.get('fiscalyear_ids', False):
            fiscalyear_ids = context['fiscalyear_ids'][0][2]
        if filter == 'filter_no':
            self.period_from = False
            self.period_to = False
            self.date_from = False
            self.date_to = False
        if filter == 'filter_date':
            if fiscalyear_ids:
                fyear = self.env['account.fiscalyear'].browse(fiscalyear_ids)
                date_from = min(fyear.mapped('date_start'))
                date_to = max(fyear.mapped('date_stop')) > time.strftime(
                    '%Y-%m-%d') and time.strftime('%Y-%m-%d') or \
                    max(fyear.mapped('date_stop'))
                if date_to < date_from:
                    date_to = date_from
            else:
                date_from, date_to = time.strftime(
                    '%Y-01-01'), time.strftime('%Y-%m-%d')
            self.period_from = False
            self.period_to = False
            self.date_from = date_from
            self.date_to = date_to
        if filter == 'filter_period' and fiscalyear_ids:
            start_period = end_period = False
            self._cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f
                                ON p.fiscalyear_id = f.id
                               WHERE f.id IN %s
                               AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f
                                ON p.fiscalyear_id = f.id
                               WHERE f.id IN %s
                               AND p.date_start < NOW()
                               AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''',
                             (tuple(fiscalyear_ids), tuple(fiscalyear_ids)))
            periods = [i[0] for i in self._cr.fetchall()]
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            self.period_from = start_period
            self.period_to = end_period
            self.date_from = False
            self.date_to = False

    @api.multi
    def run_report(self):
        raise ValidationError(_('Not implemented.'))
