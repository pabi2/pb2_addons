# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportRegistrarOfGuarantee(models.TransientModel):
    _name = 'xlsx.report.registrar.of.guarantee'
    _inherit = 'report.account.common'

    account_code = fields.Char(
        string='Account Code',
        default='2203010001,2203010002,2203010003,2203010004,2203010005',
        readonly=True,
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
        if self.account_code:
            dom += [('invoice_move_line_id.account_id.code', 'in',
                     self.account_code.split(','))]
        if self.reconcile_cond != 'all':
            if self.reconcile_cond == 'open_item':
                dom += [('invoice_move_line_id.reconcile_id', '=', False)]
            else:
                dom += [('invoice_move_line_id.reconcile_id', '!=', False)]
        if self.fiscalyear_start_id:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_move_line_id.move_id.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_move_line_id.move_id.date', '>=',
                     self.date_start)]
        if self.date_end:
            dom += [('invoice_move_line_id.move_id.date', '<=', self.date_end)]
        self.results = Result.search(dom)


class RegistrarOfGuaranteeView(models.Model):
    _name = 'registrar.of.guarantee.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    invoice_move_line_id = fields.Many2one(
        'account.move.line',
        string='Invoice Move Line',
        readonly=True,
    )
    voucher_move_line_id = fields.Many2one(
        'account.move.line',
        string='Voucher Move Line',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(
                        ORDER BY invoice_line.move_line_id,
                                 voucher_line.move_line_id) AS id,
                   invoice_line.move_line_id AS invoice_move_line_id,
                   voucher_line.move_line_id AS voucher_move_line_id
            FROM (
                (SELECT aml.id AS move_line_id,
                        aml.reconcile_id, aml.reconcile_partial_id
                 FROM account_move_line aml
                 LEFT JOIN interface_account_entry iae
                    ON aml.move_id = iae.move_id
                 WHERE iae.type in ('invoice') OR aml.doctype IN ('adjustment')
                ) invoice_line
                LEFT JOIN
                (SELECT aml.id AS move_line_id,
                        aml.reconcile_id, aml.reconcile_partial_id
                 FROM account_move_line aml
                 LEFT JOIN interface_account_entry iae
                    ON aml.move_id = iae.move_id
                 WHERE iae.type in ('voucher')) voucher_line
                 ON invoice_line.reconcile_id = voucher_line.reconcile_id
                    OR invoice_line.reconcile_partial_id
                        = voucher_line.reconcile_partial_id
            )
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
