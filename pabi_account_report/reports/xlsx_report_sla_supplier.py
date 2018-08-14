# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools


class SLASupplierView(models.Model):
    _name = 'sla.supplier.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        readonly=True,
    )
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
    )
    fiscalyear = fields.Char(
        string='Fiscal Year',
        readonly=True,
    )
    source_document_type = fields.Char(
        string='Source Document Type',
        readonly=True,
    )
    count_invoice = fields.Integer(
        string='Count Invoice',
        readonly=True,
    )
    date_due = fields.Date(
        string='Due Date',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY voucher_id) AS id, *
            FROM(
                (SELECT voucher_id, voucher_number, fiscalyear,
                        'all' AS source_document_type,
                        COUNT(invoice_id) AS count_invoice,
                        MIN(date_due) AS date_due
                 FROM pabi_common_supplier_payment_report_view
                 WHERE source_document_type IS NULL OR
                       source_document_type = 'purchase' OR
                       (source_document_type = 'expense' AND
                        pay_to = 'supplier')
                 GROUP BY voucher_id, voucher_number, fiscalyear)
                UNION ALL
                (SELECT voucher_id, voucher_number, fiscalyear,
                        source_document_type,
                        COUNT(invoice_id) AS count_invoice,
                        MIN(date_due) AS date_due
                 FROM pabi_common_supplier_payment_report_view
                 WHERE source_document_type IS NULL OR
                       source_document_type = 'purchase' OR
                       (source_document_type = 'expense' AND
                        pay_to = 'supplier')
                 GROUP BY voucher_id, voucher_number, fiscalyear,
                          source_document_type)) AS sla_purchase
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportSLASupplier(models.TransientModel):
    _name = 'xlsx.report.sla.supplier'
    _inherit = 'report.account.common'

    user_ids = fields.Many2many(
        'res.users',
        string='Validated By',
    )
    source_document_type = fields.Selection(
        [('nothing', 'Nothing'),
         ('expense', 'Expense'),
         ('purchase', 'Purchase Order')],
        string='Source Document Ref.',
    )
    results = fields.Many2many(
        'sla.supplier.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get data from pabi.common.supplier.payment.report.view
        2. Source document type = purchase or expense or null
        """
        self.ensure_one()
        Result = self.env['sla.supplier.view']
        dom = [('source_document_type', '=',
                not self.source_document_type and 'all' or
                (self.source_document_type != 'nothing' and
                 self.source_document_type or False))]
        if self.user_ids:
            dom += [('voucher_id.validate_user_id', 'in', self.user_ids.ids)]
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
            dom += [('voucher_id.date', '>=',
                     self.date_start)]
        if self.date_end:
            dom += [('voucher_id.date', '<=',
                     self.date_end)]
        self.results = Result.search(dom, order="fiscalyear,voucher_number")
