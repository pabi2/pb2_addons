# -*- coding: utf-8 -*
from openerp import models, fields, api, tools


class XLSXReportSupplierReceiptFollowUp(models.TransientModel):
    _name = 'xlsx.report.supplier.receipt.follow.up'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Account',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )
    followup_receipt = fields.Selection(
        [('following', 'Following'), ('received', 'Received')],
        string='Receipt Followup',
        required=True,
    )
    results = fields.Many2many(
        'supplier.receipt.followup.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['supplier.receipt.followup.view']
        dom = []
        if self.account_ids:
            dom += [('invoice_line_id.account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('voucher_id.partner_id', 'in', self.partner_ids.ids)]
        if self.followup_receipt:
            dom += [('voucher_id.followup_receipt', '=',
                     self.followup_receipt)]
        if self.fiscalyear_start_id:
            dom += [('voucher_id.period_id.fiscalyear_id.date_start', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('voucher_id.period_id.fiscalyear_id.date_stop', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('voucher_id.period_id.date_start', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('voucher_id.period_id.date_stop', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('voucher_id.date_value', '>=', self.date_start)]
        if self.date_end:
            dom += [('voucher_id.date_value', '<=', self.date_end)]
        self.results = Result.search(
            dom, order="partner_id,voucher_id,invoice_id")


class SupplierReceiptFollowUpView(models.Model):
    _name = 'supplier.receipt.followup.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string='Voucher',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True,
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice Line',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY av.id, inv.id, inv_line.id)
                        AS id,
                   av.id AS voucher_id,
                   inv.id AS invoice_id,
                   inv_line.id AS invoice_line_id,
                   av.partner_id
            FROM account_voucher av
            LEFT JOIN account_voucher_line av_line ON
                av.id = av_line.voucher_id
            LEFT JOIN account_move_line am_line ON
                av_line.move_line_id = am_line.id
            LEFT JOIN account_invoice inv ON am_line.move_id = inv.move_id
            LEFT JOIN account_invoice_line inv_line ON
                inv.id = inv_line.invoice_id
            WHERE av.type = 'payment' AND av.state = 'posted'
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
