# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta


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
            WHERE ac.type ='receivable' AND am_line.reconcile_id IS NULL
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportReceivableBeforeDue(models.TransientModel):
    _name = 'xlsx.report.receivable.before.due'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_before_due_date', 'Before Due Date'),
         ('filter_date_due', 'Due Date')],
        required=True,
        default='filter_no',
    )
    date_due = fields.Date(
        string='Due Date',
    )
    before_due_date = fields.Integer(
        string='Before Due Date',
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

    @api.onchange('filter')
    def _onchange_filter(self):
        self.date_due = False
        self.before_due_date = False

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['receivable.before.due.view']
        dom = []
        if self.before_due_date:
            date_start = datetime.strptime(fields.Date.context_today(self),
                                           '%Y-%m-%d').date()
            date_end = date_start + relativedelta(days=self.before_due_date)
            dom += [('move_line_id.date_maturity', '=',
                     date_end.strftime('%Y-%m-%d'))]
        if self.date_due:
            dom += [('move_line_id.date_maturity', '=', self.date_due)]
        if self.system_ids:
            dom += [('move_line_id.system_id', 'in', self.system_ids.ids)]
        self.results = Result.search(dom)
