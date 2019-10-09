# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import datetime
import numpy as np


class SLAEmployeeView(models.Model):
    _name = 'sla.employee.view'
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
    voucher_line_id = fields.Many2one(
        'account.voucher.line',
        string='Voucher Line',
        readonly=True,
    )
    expense_id = fields.Many2one(
        'hr.expense.expense',
        string='Expense',
        readonly=True,
    )
    fiscalyear = fields.Char(
        string='Fiscal Year',
        readonly=True,
    )
    voucher_number = fields.Char(
        string='Voucher Number',
        readonly=True,
    )
    invoice_number = fields.Char(
        string='Invoice Number',
        readonly=True,
    )
    pay_to = fields.Selection(
        [('employee', 'Employee'),
         ('supplier', 'Supplier'),
         ('pettycash', 'Petty Cash'),
         ('internal', 'Internal Charge')],
        string='Pay Type',
        readonly=True,
    )
    source_document_type = fields.Selection(
        [('purchase', 'Purchase Order'),
         ('sale', 'Sales Order'),
         ('expense', 'Expense'),
         ('advance', 'Advance')],
        string='Source Document Type',
        readonly=True,
    )
    date_due = fields.Date(
        string='Due Date',
        readonly=True,
    )
    salary_number = fields.Char(
        string='Salary Number',
    )
    business_day = fields.Integer(
        string='Business Day',
        compute='_compute_business_day',
    )

    @api.multi
    def _compute_business_day(self):
        holidays = self.env['calendar.event'].search(
            [('user_id.login', '=', 'holiday')]).mapped('start_date')
        for rec in self:
            if not rec.invoice_id.source_document_id:
                continue
            # --
            date_start = False
            if rec.invoice_id.source_document_id._name == 'hr.expense.expense':
                date_start = rec.invoice_id.source_document_id.date_valid
            date_end = rec.voucher_id.payment_export_id.date_value
            if date_start and date_end:
                if date_end >= date_start:
                    date_end = (datetime.datetime.strptime(
                                date_end, '%Y-%m-%d')
                                + datetime.timedelta(days=1)) \
                                .strftime('%Y-%m-%d')
                else:
                    date_start = (datetime.datetime.strptime(
                                  date_start, '%Y-%m-%d')
                                  + datetime.timedelta(days=1)) \
                                  .strftime('%Y-%m-%d')
                rec.business_day = np.busday_count(
                    date_start, date_end, holidays=holidays)

    def _get_sql_select(self):
        sql_select = """
            ROW_NUMBER() OVER(ORDER BY av.id, ai.id) AS id,
            av.id AS voucher_id, ai.id AS invoice_id,
            av_line.id AS voucher_line_id, ex.id AS expense_id,
            af.name AS fiscalyear, av.number AS voucher_number,
            ai.number AS invoice_number, ex.pay_to, ai.source_document_type,
            ai.date_due, am_line.doctype as doctype, sl.number as salary_number
        """
        return sql_select

    def _get_sql_view(self):
        sql_select = """
            SELECT %s
            FROM account_voucher av
            LEFT JOIN account_voucher_line av_line
                ON av.id = av_line.voucher_id
            LEFT JOIN account_move_line am_line
                ON av_line.move_line_id = am_line.id
            LEFT JOIN account_invoice ai ON am_line.move_id = ai.move_id
            LEFT JOIN account_period ap ON av.period_id = ap.id
            LEFT JOIN account_fiscalyear af ON ap.fiscalyear_id = af.id
            LEFT JOIN payment_export pe ON av.payment_export_id = pe.id
            LEFT JOIN hr_expense_expense ex ON ai.expense_id = ex.id
            LEFT JOIN hr_salary_expense sl ON sl.move_id = am_line.move_id
            
            LEFT JOIN res_partner rp ON ai.partner_id = rp.id
            LEFT JOIN res_partner_category rpc ON rp.category_id = rpc.id
            
            WHERE av.type = 'payment' AND av.state = 'posted'
                AND pe.state = 'done' AND rpc.name in ('Supplier-ภาครัฐ','Supplier-ภาคเอกชน','ต่างประเทศ','พนักงาน สวทช.')
                OR am_line.doctype = 'salary_expense'
        """ % (self._get_sql_select())
        #AND ex.pay_to != 'supplier' 
        return sql_select
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))

# class PabiCommonSupplierPaymentReportView(models.Model):
#     _inherit = 'pabi.common.supplier.payment.report.view'
#
#     business_day = fields.Integer(
#         string='Business Day',
#         compute='_compute_business_day',
#     )
#
#     @api.multi
#     def _compute_business_day(self):
#         holidays = self.env['calendar.event'].search(
#             [('user_id.login', '=', 'holiday')]).mapped('start_date')
#         for rec in self:
#             if not rec.invoice_id.source_document_id:
#                 continue
#             # --
#             date_start = False
#             if rec.invoice_id.source_document_id._name == 'hr.expense.expense':
#                 date_start = rec.invoice_id.source_document_id.date_valid
#             date_end = rec.voucher_id.payment_export_id.date_value
#             if date_start and date_end:
#                 if date_end >= date_start:
#                     date_end = (datetime.datetime.strptime(
#                                 date_end, '%Y-%m-%d')
#                                 + datetime.timedelta(days=1)) \
#                                 .strftime('%Y-%m-%d')
#                 else:
#                     date_start = (datetime.datetime.strptime(
#                                   date_start, '%Y-%m-%d')
#                                   + datetime.timedelta(days=1)) \
#                                   .strftime('%Y-%m-%d')
#                 rec.business_day = np.busday_count(
#                     date_start, date_end, holidays=holidays)


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
        'sla.employee.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    supplier_category_name = fields.Selection(
        [('employee', 'พนักงาน สวทช'),
         ('supplier', 'Supplier ภายนอก'),
         ('foreign', 'Supplier ต่างประเทศ')],
        string='Supplier Category',
    )
    async_process = fields.Boolean(
        string='Run task in background?',
        default=True,
    )

    @api.multi
    def _compute_results(self):
        """
        Solution
        1. Get data from sla.employee.view
        2. Source document type = advance or expense
        3. Pay type != supplier
        """
        self.ensure_one()
        Result = self.env['sla.employee.view']
        dom = []
        if self.supplier_category_name:
            if self.supplier_category_name == 'employee':
                dom += [('pay_to', '=', 'employee')]
            elif self.supplier_category_name == 'supplier':
                dom += [('pay_to', '!=', 'employee'),('invoice_id.partner_id.category_id.name', '!=', 'ต่างประเทศ')]
            elif self.supplier_category_name == 'foreign':
                dom += [('pay_to', '!=', 'employee'),('invoice_id.partner_id.category_id.name', '=', 'ต่างประเทศ')]
        if self.user_ids:
            dom += [('voucher_id.validate_user_id', 'in', self.user_ids.ids)]
        if self.source_document_type:
            dom += [('invoice_id.source_document_type', '=',
                     self.source_document_type)]
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
