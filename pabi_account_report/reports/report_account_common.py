# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
import time

PREFIX_DOCTYPE = {'in_invoice': 'KV',
                  'in_refund': 'CN',
                  'out_invoice': 'DV',
                  'out_refund': 'SN',
                  'payment': 'PV',
                  'receipt': 'RC',
                  'adjustment': 'JN',
                  'incoming_shipment': 'IN',
                  'interface_account': 'IA'}


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
        date_end = self.fiscalyear_end_id.date_stop
        if date_start or date_end:
            if not date_start:
                fiscalyear = Fiscalyear.search(
                    [('company_id', '=', self.company_id.id)],
                    order="date_start", limit=1)
                date_start = fiscalyear.date_start
            if not date_end:
                fiscalyear = Fiscalyear.search(
                    [('company_id', '=', self.company_id.id)],
                    order="date_stop desc", limit=1)
                date_end = fiscalyear.date_stop
        self.fiscalyear_date_start = date_start
        self.fiscalyear_date_end = date_end

    @api.multi
    def _reset_common_field(self):
        self.ensure_one()
        if not self._context.get('reset_common_field', False):
            return False
        self.fiscalyear_start_id = False
        self.fiscalyear_end_id = False
        self.period_start_id = False
        self.period_end_id = False
        self.date_start = False
        self.date_end = False
        return True

    @api.onchange('chart_account_id')
    def _onchange_chart_account_id(self):
        # Reset common field
        if self._reset_common_field():
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
                 ('special', '=', False)], order="date_start", limit=1)
            period_end = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 ('date_start', '<=', now), ('date_stop', '>=', now),
                 ('special', '=', False)], limit=1)
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
            if now >= fiscalyear_date_start and now <= fiscalyear_date_end:
                period_start = Period.find(dt=fiscalyear_date_start)[0]
                period_end = Period.find(dt=now)[0]
                date_start = fiscalyear_date_start
                date_end = now
            elif fiscalyear_date_end < now:
                period_start = Period.find(dt=fiscalyear_date_start)[0]
                period_end = Period.find(dt=fiscalyear_date_end)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_end
            elif fiscalyear_date_start > now:
                period_start = Period.find(dt=fiscalyear_date_start)[0]
                period_end = Period.find(dt=fiscalyear_date_start)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_start
        return period_start, period_end, date_start, date_end

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
        # Reset common field
        if self._reset_common_field():
            return {}
        # --
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

    @api.multi
    def run_report(self):
        raise ValidationError(_('Not implemented.'))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    prefix_doctype = fields.Char(
        string='Prefix Document Type',
        compute='_compute_prefix_doctype',
    )

    @api.multi
    def _compute_prefix_doctype(self):
        for rec in self:
            rec.prefix_doctype = PREFIX_DOCTYPE.get(rec.doctype, False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    prefix_doctype = fields.Char(
        string='Prefix Document Type',
        compute='_compute_prefix_doctype',
    )

    @api.multi
    def _compute_prefix_doctype(self):
        for rec in self:
            rec.prefix_doctype = PREFIX_DOCTYPE.get(rec.doctype, False)
