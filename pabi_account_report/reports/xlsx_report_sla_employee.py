# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportSLAEmployee(models.TransientModel):
    _name = 'xlsx.report.sla.employee'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Validated By',
    )
    source_document_type = fields.Selection(
        [('expense', 'Expense'),
         ('advance', 'Advance')],
        string='Source Document Ref.',
    )
    results = fields.Many2many(
        'pabi.common.account.voucher.report.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['pabi.common.account.voucher.report.view']
        dom = [('voucher_id.type', '=', 'payment'),
               ('voucher_id.state', '=', 'posted'),
               ('voucher_id.payment_export_id.state', '=', 'done'),
               ('invoice_id.source_document_type', 'in',
                ['advance', 'expense'])]
        if self.user_ids:
            dom += [('voucher_id.validate_user_id', 'in', self.user_ids.ids)]
        if self.source_document_type:
            dom += [('invoice_id.source_document_type', '=',
                     self.source_document_type or False)]
        if self.fiscalyear_start_id:
            dom += [('voucher_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('voucher_id.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('voucher_id.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('voucher_id.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('voucher_id.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('voucher_id.date', '<=', self.date_end)]
        self.results = Result.search(
            dom, order="fiscalyear,voucher_number,invoice_number")
