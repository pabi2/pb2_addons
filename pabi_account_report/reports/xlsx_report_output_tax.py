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
        model = 'account.tax.report'
        where = "doc_type = 'sale' \
                 and (move_id is not null or invoice_tax_id is not null or \
                 voucher_tax_id is not null)"
        if self.calendar_period_id:
            where += " and report_period_id = %s" \
                % (str(self.calendar_period_id.id))
        if self.taxbranch_id:
            where += " and taxbranch_id = %s" % (str(self.taxbranch_id.id))
        if self.tax == 'o7':
            where += " and tax in ('O7', 'OI7')"
        if self.tax == 'o0':
            where += " and tax = 'O0'"
        self._cr.execute("""
            select id from %s where %s""" % (model.replace('.', '_'), where))
        report_ids = map(lambda l: l[0], self._cr.fetchall())
        # --
        Result = self.env[model]
        dom = [('id', '=', 0)]
        if report_ids:
            dom = [('id', 'in', report_ids)]
        self.results = Result.search(dom, order='number_preprint')
