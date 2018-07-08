# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportContractCollateral(models.TransientModel):
    _name = 'xlsx.report.contract.collateral'
    _inherit = 'report.account.common'

    date_report = fields.Date(
        string='Report Date',
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    filter = fields.Selection(
        default='filter_date',
        readonly=True,
    )
    results = fields.Many2many(
        'purchase.contract',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['purchase.contract']
        dom = []
        if self.date_report:
            dom += [('collateral_remand_date', '>=', self.date_report)]
        if self.partner_ids:
            dom += [('supplier_id', 'in', self.partner_ids.ids)]
        self.results = Result.search(dom)
