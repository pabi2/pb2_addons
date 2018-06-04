# -*- coding: utf-8 -*
from openerp import models, fields, api


class XLSXReportInputTax(models.TransientModel):
    _name = 'xlsx.report.input.tax'
    _inherit = 'xlsx.report'

    calendar_period_id = fields.Many2one(
        'account.period.calendar',
        string='Period',
        required=True,
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        required=True,
    )
    results = fields.Many2many(
        'account.tax.report',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.tax.report']
        dom = [('doc_type', '=', 'purchase')]
        if self.calendar_period_id:
            dom += [('period_id', '=', self.calendar_period_id.id)]
        if self.taxbranch_id:
            dom += [('taxbranch_id', '=', self.taxbranch_id.id)]
        self.results = Result.search(dom, order='invoice_date')
