# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportSLAReceipt(models.TransientModel):
    _name = 'xlsx.report.sla.receipt'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Validated By',
    )
    results = fields.Many2many(
        'account.bank.receipt',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.bank.receipt']
        dom = [('state', '=', 'done')]
        if self.user_ids:
            dom += [('validate_user_id', 'in', self.user_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('move_id.date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('move_id.date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('move_id.date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('move_id.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('move_id.date', '<=', self.date_end)]
        self.results = Result.search(dom, order="name")
