# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import datetime
import numpy as np

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
    
    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        
        where_str = 'and'.join(where_dom)
        where_str = where_str.replace(',)',')')
        return where_str
    
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
        dom = [('rpc.name', 'in', ('Supplier-ภาครัฐ','Supplier-ภาคเอกชน','ต่างประเทศ','พนักงาน สวทช.'))]
        if self.supplier_category_name:
            if self.supplier_category_name == 'employee':
                dom += [('ex.pay_to', '=', 'employee')]
            elif self.supplier_category_name == 'supplier':
                dom += [('ex.pay_to', '!=', 'employee'),('ai_part_cate.name', '!=', 'ต่างประเทศ')]
            elif self.supplier_category_name == 'foreign':
                dom += [('ex.pay_to', '!=', 'employee'),('ai_part_cate.name', '=', 'ต่างประเทศ')]
        if self.user_ids:
            dom += [('av.validate_user_id', 'in', self.user_ids.ids)]
        if self.source_document_type:
            dom += [('ai.source_document_type', '=',
                     self.source_document_type)]
        if self.fiscalyear_start_id:
            dom += [('av.date', '>=',
                     self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('av.date', '<=',
                     self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('av.date', '>=',
                     self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('av.date', '<=',
                     self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('av.date', '>=', self.date_start)]
        if self.date_end:
            dom += [('av.date', '<=', self.date_end)]
        
        where_str = self._domain_to_where_str(dom)
        
        self._cr.execute("""
            SELECT 
                ROW_NUMBER() OVER(ORDER BY av.id, ai.id) AS id,
                av.id AS voucher_id, ai.id AS invoice_id,
                av_line.id AS voucher_line_id, ex.id AS expense_id,
                af.name AS fiscalyear, av.number AS voucher_number,
                ai.number AS invoice_number, ex.pay_to, ai.source_document_type,
                ai.date_due, am_line.doctype as doctype, sl.number as salary_number
            FROM account_voucher av
            LEFT JOIN account_voucher_line av_line
                ON av.id = av_line.voucher_id
            LEFT JOIN account_move_line am_line
                ON av_line.move_line_id = am_line.id
            LEFT JOIN account_invoice ai ON am_line.move_id = ai.move_id
            LEFT JOIN res_partner ai_part ON ai_part.id = ai.partner_id
            LEFT JOIN res_partner_category ai_part_cate ON ai_part_cate.id = ai_part.category_id
            LEFT JOIN account_period ap ON av.period_id = ap.id
            LEFT JOIN account_fiscalyear af ON ap.fiscalyear_id = af.id
            LEFT JOIN payment_export pe ON av.payment_export_id = pe.id
            LEFT JOIN hr_expense_expense ex ON ai.expense_id = ex.id
            LEFT JOIN hr_salary_expense sl ON sl.move_id = am_line.move_id
            LEFT JOIN res_partner rp ON ai.partner_id = rp.id
            LEFT JOIN res_partner_category rpc ON rp.category_id = rpc.id
            WHERE av.type = 'payment' AND av.state = 'posted'
                AND (pe.state = 'done' OR av.payment_export_id is null)
                AND %s
            """ % (where_str)) #OR am_line.doctype = 'salary_expense'
            
        sla_emp = self._cr.dictfetchall()
        
        for line in sla_emp:
            self.results += Result.new(line)

class SLAEmployeeView(models.AbstractModel):
    _name = 'sla.employee.view'

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
    pay_to = fields.Char(
        string='Pay Type',
        readonly=True,
    )
    source_document_type = fields.Char(
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

