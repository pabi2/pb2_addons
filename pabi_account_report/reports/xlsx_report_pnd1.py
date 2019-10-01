# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class XLSXReportPND1(models.TransientModel):
    _name = 'xlsx.report.pnd1'
    _inherit = 'report.account.common'
    
    filter = fields.Selection(
        readonly=True,
        default='filter_period',
    )
    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Calendar Period',
        required=True,
        default=lambda self: self.env['account.period.calendar'].find()
    )
    results = fields.Many2many(
        'personal.income.tax',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    @api.onchange('fiscalyear_start_id', 'fiscalyear_end_id')
    def _onchange_fiscalyear_id(self):
        if self.fiscalyear_start_id and self.fiscalyear_end_id:
            domain = [('company_id', '=', self.company_id.id),
                      ('date_start', '>=', (datetime.strptime(str(self.fiscalyear_start_id.date_start), '%Y-%m-%d')-relativedelta(months=3)).strftime('%Y-%m-%d')), 
                      ('date_stop', '<=', self.fiscalyear_end_id.date_stop)]
        else:
            domain =  [('company_id', '=', self.company_id.id)]
            
        return {'domain': {'calendar_period_id': domain}}

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['personal.income.tax']
        dom = [('amount_wht', '!=', 0.0)]
        if self.calendar_period_id:
            dom += [('date', '>=', self.calendar_period_id.date_start),
                    ('date', '<=', self.calendar_period_id.date_stop)]
        self.results = Result.search(dom, order='date, id')
