# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportRegistrarOfGuarantee(models.TransientModel):
    _name = 'xlsx.report.registrar.of.guarantee'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
    )
    reconcile_cond = fields.Selection(
        [('all', 'All Items'),
         ('open_item', 'Open Items'),
         ('reconciled', 'Full Reconciled')],
        string='Reconciled',
        default='all',
        required=True,
    )
    results = fields.Many2many(
        'registrar.of.guarantee.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['registrar.of.guarantee.view']
        dom = []
        if self.account_ids:
            dom += [('move_line_id.account_id', 'in', self.account_ids.ids)]
        if self.reconcile_cond != 'all':
            if self.reconcile_cond == 'open_item':
                dom += [('move_line_id.reconcile_id', '=', False)]
            else:
                dom += [('move_line_id.reconcile_id', '!=', False)]
        if self.fiscalyear_start_id:
            dom += [('move_line_id.move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('move_line_id.move_id.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('move_line_id.move_id.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('move_line_id.move_id.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('move_line_id.move_id.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('move_line_id.move_id.date', '<=', self.date_end)]
        self.results = Result.search(dom)


class RegistrarOfGuaranteeView(models.Model):
    _name = 'registrar.of.guarantee.view'
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
    payment_id = fields.Many2one(
        'account.voucher',
        string='Payment',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY l.id, pv.payment_id) AS id,
                   l.id AS move_line_id, pv.payment_id
            FROM account_move_line l
            LEFT JOIN account_invoice inv ON l.move_id = inv.move_id
            LEFT JOIN (SELECT avl.invoice_id, av.id AS payment_id
                       FROM account_voucher_line avl
                       LEFT JOIN account_voucher av ON avl.voucher_id = av.id
                       WHERE av.state = 'posted') pv ON inv.id = pv.invoice_id
            WHERE l.doctype IN ('out_invoice', 'out_refund', 'adjustment')
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
