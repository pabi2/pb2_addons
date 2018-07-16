# -*- coding: utf-8 -*-
# from openerp import models, fields, api, tools
from openerp import models, fields, api


class XLSXReportGlAllowanceDoubtfulAccounts(models.TransientModel):
    _name = 'xlsx.report.gl.allowance.doubtful.accounts'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    allowance_for_doubful_account_code = fields.Char(
        string='Account Code',
        readonly=True,
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = [('move_id.state', '=', 'posted'),
               ('account_id.code', '=',
               self.allowance_for_doubful_account_code),
               ('move_id.date', '<=', self.date_report)]
        self.results = Result.search(dom)
