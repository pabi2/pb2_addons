# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import time


class JasperReportAccountGL_Common(models.AbstractModel):
    _name = 'jasper.report.account.gl.common'

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
    count_chartfield = fields.Integer(
        compute='_compute_count_chartfield',
        string='Budget Count',
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=['|',('active', '=', False),('active', '=', True),('model', '!=', 'res.personnel.costcenter')],
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
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
        # For filter period by fiscalyear
        self.ensure_one()
        Fiscalyear = self.env['account.fiscalyear']
        date_start = self.fiscalyear_start_id.date_start
        date_end = self.fiscalyear_end_id.date_stop
        if date_start or date_end:
            domain = [('company_id', '=', self.company_id.id)]
            if not date_start:
                fiscalyear = Fiscalyear.search(
                    domain, order="date_start", limit=1)
                date_start = fiscalyear.date_start
            if not date_end:
                fiscalyear = Fiscalyear.search(
                    domain, order="date_stop desc", limit=1)
                date_end = fiscalyear.date_stop
        self.fiscalyear_date_start = date_start
        self.fiscalyear_date_end = date_end

    @api.onchange('chart_account_id')
    def _onchange_chart_account_id(self):
        if not self.chart_account_id:
            return {}
        # --
        company = self.chart_account_id.company_id
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', company.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        self.company_id = company
        self.fiscalyear_start_id = fiscalyear
        self.fiscalyear_end_id = fiscalyear
        if self.filter == "filter_period":
            Period = self.env['account.period']
            period_start = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 # ('special', '=', False)
                 ], order="code", limit=1)
            period_end = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 ('date_start', '<=', now), ('date_stop', '>=', now),
                 # ('special', '=', False)
                 ], limit=1)
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = fiscalyear.date_start
            self.date_end = fiscalyear and now or False

    @api.multi
    def _get_common_period_and_date(self):
        self.ensure_one()
        period_start = period_end = False
        date_start = date_end = False
        now = time.strftime('%Y-%m-%d')
        fiscalyear_date_start = self.fiscalyear_date_start
        fiscalyear_date_end = self.fiscalyear_date_end
        Period = self.env['account.period'].with_context(
            company_id=self.company_id.id)
        if fiscalyear_date_start and fiscalyear_date_end and \
           fiscalyear_date_end >= fiscalyear_date_start:
            ctx = {'account_period_prefer_normal': False}
            if now >= fiscalyear_date_start and now <= fiscalyear_date_end:
                period_start = \
                    Period.with_context(ctx).find(dt=fiscalyear_date_start) \
                    .sorted(key=lambda l: l.code)[0]
                period_end = Period.find(dt=now)[0]
                date_start = fiscalyear_date_start
                date_end = now
            elif fiscalyear_date_end < now:
                period_start = \
                    Period.with_context(ctx).find(dt=fiscalyear_date_start) \
                    .sorted(key=lambda l: l.code)[0]
                period_end = Period.find(dt=fiscalyear_date_end)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_end
            elif fiscalyear_date_start > now:
                period_start = \
                    Period.with_context(ctx).find(dt=fiscalyear_date_start) \
                    .sorted(key=lambda l: l.code)[0]
                period_end = Period.find(dt=fiscalyear_date_start)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_start
        return period_start, period_end, date_start, date_end

    @api.multi
    @api.depends('chartfield_ids')
    def _compute_count_chartfield(self):
        for rec in self:
            rec.count_chartfield = len(rec.chartfield_ids)

    @api.onchange('fiscalyear_start_id', 'fiscalyear_end_id')
    def _onchange_fiscalyear_id(self):
        period_start, period_end, date_start, date_end = \
            self._get_common_period_and_date()
        if self.filter == "filter_period":
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = date_start
            self.date_end = date_end

    @api.onchange('filter')
    def _onchange_filter(self):
        period_start, period_end, date_start, date_end = \
            self._get_common_period_and_date()
        self.period_start_id = self.period_end_id = False
        self.date_start = self.date_end = False
        if self.filter == "filter_period":
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = date_start
            self.date_end = date_end

    @api.onchange('line_filter')
    def _onchange_line_filter(self):
        self.chartfield_ids = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.line_filter:
            codes = self.line_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.chartfield_ids = Chartfield.search(dom, order='id')

    @api.multi
    def start_report(self):
        raise ValidationError(_('Not implemented.'))
