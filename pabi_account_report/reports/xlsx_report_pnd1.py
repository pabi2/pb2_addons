# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
        default=lambda self: self.env['account.period.calendar'].find(),
    )
    results = fields.Many2many(
        'personal.income.tax',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['personal.income.tax']
        dom = [('amount_wht', '!=', 0.0)]
        if self.calendar_period_id:
            dom += [('date', '>=', self.calendar_period_id.date_start),
                    ('date', '<=', self.calendar_period_id.date_stop)]
        self.results = Result.search(dom, order='date, id')
        print len(self.results)
