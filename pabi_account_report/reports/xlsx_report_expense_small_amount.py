# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools

class AssetRepairView(models.Model):
    _name = 'xlsx.report.expense.small.amount.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    partner_taxid = fields.Char(
        string='Partner Tax',
    )
    partner_name = fields.Char(
        string='Partner Name',
    )
    name = fields.Char(
        string='Name',
    )
    base = fields.Float(
        string='Base',
    )
    invoice_date = fields.Date(
        string='Invoice Date',
    )
    partner_invoice_number = fields.Char(
        string='Tax Invoice Number',
        size=500,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    source_document = fields.Char(
        string='Source Document Ref.',
        size=500,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
    )
    invoice_number = fields.Char(
        string='Invoice Number',
    )
    tax_detail_id = fields.Many2one(
        'account.tax.detail',
        string='Tax Detail',
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
    )
    tax_sequence_display = fields.Char(
        string='Sequence',
    )
    invoice_tax_id = fields.Many2one(
        'account.invoice.tax',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )
    docline_seq = fields.Integer(
        string='Docline Seq',
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Journal Item'
    )
    debit = fields.Float(
        string='Debit',
    )
    ref = fields.Char(
        string='Ref',
        readonly=True,
    )
    def _get_sql_view(self):
        sql_view = """
            SELECT 
                ROW_NUMBER() OVER(ORDER BY source_document,invoice_date) AS id,
                    iv1.move_id,
                    invoice_number,
                    tax_detail_id,
                    period_id,
                    partner_id,
                    partner_taxid,
                    partner_name,
                    tax_sequence_display,
                    source_document,
                    partner_invoice_number,
                    invoice_date,
                    base,
                    invoice_tax_id,
                    invoice_id,
                    docline_seq,
                    move_line_id,
                    name,
                    debit,
                    ref
                FROM public.account_invoice_tax_report iv1 
                LEFT JOIN account_invoice_line_tax_focus iv2 on iv2.move_id = iv1.move_id
                WHERE iv1.period_id =46
                and name is not null
                and debit = base
                AND source_document like 'EX%'
                order by source_document,invoice_date
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))

class XLSXReportInputTax(models.TransientModel):
    _name = 'xlsx.report.expense.small.amount'
    _inherit = 'report.account.common'

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners'
    )

    results = fields.Many2many(
        'xlsx.report.expense.small.amount.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
 
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.expense.small.amount.view']
        dom = []
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.period_start_id:
            dom += [('invoice_date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('invoice_date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('invoice_date', '>=', self.date_start)]
        if self.date_end:
            dom += [('invoice_date', '<=', self.date_end)]
        self.results = Result.search(dom)
