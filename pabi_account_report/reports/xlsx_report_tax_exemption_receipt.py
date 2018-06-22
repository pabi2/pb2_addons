# -*- coding: utf-8 -*
from openerp import models, fields, api


class XLSXReportOutputTax(models.TransientModel):
    _name = 'xlsx.report.tax.exemption.receipt'
    _inherit = 'report.account.common'

    fiscalyear_start_id = fields.Many2one(
        default=False,
    )
    fiscalyear_end_id = fields.Many2one(
        default=False,
    )
    filter = fields.Selection(
        readonly=True,
        default='filter_period',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        required=True,
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Taxbranch',
        required=True,
    )
    results = fields.Many2many(
        'account.invoice',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.invoice']
        dom = [('type','in',['out_invoice', 'out_refund']), ('tax_line', '=', False), ('state','not in',['draff','cancel'])]
        if self.period_id:
            dom += [('period_id', '=', self.period_id.id)]
        if self.taxbranch_id:
            dom += [('taxbranch_id', '=', self.taxbranch_id.id)]
        self.results = Result.search(dom, order='number_preprint')
