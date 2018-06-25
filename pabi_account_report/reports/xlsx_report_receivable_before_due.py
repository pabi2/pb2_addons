# -*- coding: utf-8 -*
from openerp import models, fields, api, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta


class XLSXReportReceivableBeforeDue(models.TransientModel):
    _name = 'xlsx.report.receivable.before.due'
    _inherit = 'report.account.common'

    fiscalyear_start_id = fields.Many2one(
        default=False,
    )
    fiscalyear_end_id = fields.Many2one(
        default=False,
    )
    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    date_report = fields.Date(
        string='Report Date',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    before_due_date = fields.Integer(
        string='Before Due Date',
        required=True,
    )
    system_ids = fields.Many2many(
        'interface.system',
        string='System Origin',
    )
    results = fields.Many2many(
        'receivable.before.due.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['receivable.before.due.view']
        dom = []
        date_start = datetime.strptime(self.date_report, '%Y-%m-%d').date()
        date_end = date_start + relativedelta(days=self.before_due_date)
        if self.system_ids:
            dom += [('move_line_id.system_id', 'in', self.system_ids.ids)]
        dom += [('move_line_id.date_maturity', '=',
                 date_end.strftime('%Y-%m-%d'))]
        self.results = Result.search(dom)


class ReceivableBeforeDueView(models.Model):
    _name = 'receivable.before.due.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY am.id) AS id,
                   am_line.id AS move_line_id
            FROM account_move am
            LEFT JOIN account_move_line am_line ON am.id = am_line.move_id
            LEFT JOIN account_account ac ON am_line.account_id = ac.id
            WHERE ac.type ='receivable' and am_line.reconcile_id is null
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
