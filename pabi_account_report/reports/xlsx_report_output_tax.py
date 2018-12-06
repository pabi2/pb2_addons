# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportOutputTax(models.TransientModel):
    _name = 'xlsx.report.output.tax'
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
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        required=True,
    )
    tax = fields.Selection(
        [('o0', 'O0'),
         ('o7', 'O7')],
        string='Tax',
    )
    results = fields.Many2many(
        'account.tax.report',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get from account.tax.report
        2. Check document type is sale (doc_type = sale)
        """
        self.ensure_one()
        Result = self.env['account.tax.report']
        dom = [('doc_type', '=', 'sale'), '|', ('move_id', '!=', False),
               ('invoice_tax_id', '!=', False), '|',
               ('voucher_tax_id', '!=', False)]
        if self.calendar_period_id:
            dom += [('report_period_id', '=', self.calendar_period_id.id)]
        if self.taxbranch_id:
            dom += [('taxbranch_id', '=', self.taxbranch_id.id)]
        if self.tax == 'o7':
            dom += [('tax', 'in', ['O7', 'OI7'])]
        if self.tax == 'o0':
            dom += [('tax', '=', 'O0')]
        self.results = Result.search(dom, order='number_preprint')
