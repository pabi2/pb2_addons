# -*- coding: utf-8 -*-
from openerp import models, fields, api
import time
import pandas as pd




class XLSXReportPayableDetailView(models.AbstractModel):
    _name = 'xlsx.report.payable.detail.view'
    _inherit = 'account.move.line'

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
    )
    tax_code = fields.Many2one(
        string='Tax Code',
    )
    move_name = fields.Text(
        string='Move Name',
    )
    transfer_type = fields.Text(
        string='Transfer Type',
    )
    payment_export_name = fields.Many2one(
        string='Payment Export Name',
    )
    number_cheque = fields.Text(
        string='Cheque Number',
    )
    income_tax = fields.Text(
        string='Income Tax',
    )
    payment_amount = fields.Float(
        string='Invoice Amount',
    )
    sum_amount = fields.Float(
        string='Sum Amount',
    )
    


class XLSXReportPayableDetail(models.TransientModel):
    _name = 'xlsx.report.payable.detail'
    _inherit = 'report.account.common'

    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    as_of_date = fields.Date(
        string='As of Date',
    )
    period_length_days = fields.Integer(
        string='Period Length (days)',
        default=30,
        required=True,
    )
    move_ids = fields.Many2many(
        'account.move',
        string='Document Numbers',
    )
    filter = fields.Selection(
        selection_add=[('filter_as_of_date', 'As of Date')],
    )
    date_start_real = fields.Date(
        string='Real Start Date',
        compute='_compute_date_real',
    )
    date_end_real = fields.Date(
        string='Real End Date',
        compute='_compute_date_real',
    )
    results = fields.Many2many(
        'xlsx.report.payable.detail.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.onchange('filter')
    def _onchange_filter(self):
        super(XLSXReportPayableDetail, self)._onchange_filter()
        self.as_of_date = False
        if self.filter == "filter_as_of_date":
            self.as_of_date = time.strftime('%Y-%m-%d')
            self.fiscalyear_start_id = self.fiscalyear_end_id = False

    @api.model
    def _get_date_list(self, date_start, date_end):
        return [x.strftime("%Y-%m-%d") for x in pd.date_range(date_start,
                                                              date_end)]

    @api.multi
    def _compute_date_real(self):
        self.ensure_one()
        Fiscalyear = self.env['account.fiscalyear']
        date_start = Fiscalyear.search(
            [('company_id', '=', self.company_id.id)],
            order="date_start", limit=1).date_start
        date_end = Fiscalyear.search(
            [('company_id', '=', self.company_id.id)],
            order="date_stop desc", limit=1).date_stop
        date_list = self._get_date_list(date_start, date_end)
        if self.fiscalyear_start_id:
            date_fiscalyear_start = self.fiscalyear_start_id.date_start
            temp_date_list = self._get_date_list(date_fiscalyear_start,
                                                 date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.fiscalyear_end_id:
            date_fiscalyear_end = self.fiscalyear_end_id.date_stop
            temp_date_list = self._get_date_list(date_start,
                                                 date_fiscalyear_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.period_start_id:
            date_period_start = self.period_start_id.date_start
            temp_date_list = self._get_date_list(date_period_start, date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.period_end_id:
            date_period_end = self.period_end_id.date_stop
            temp_date_list = self._get_date_list(date_start, date_period_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.date_start:
            temp_date_list = self._get_date_list(self.date_start, date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.date_end:
            temp_date_list = self._get_date_list(date_start, self.date_end)
            date_list = list(set(date_list) & set(temp_date_list))
        if self.as_of_date:
            temp_date_list = self._get_date_list(date_start, self.as_of_date)
            date_list = list(set(date_list) & set(temp_date_list))
        try:
            self.date_start_real = min(date_list)
            self.date_end_real = max(date_list)
        except Exception:
            self.date_start_real = self.date_end_real = False

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = [#('account_id.type', '=', 'payable'),
               #('date_maturity', '!=', False),
               ('move_id.state', '=', 'posted')]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.move_ids:
            dom += [('move_id', 'in', self.move_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('date', '>=', self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('date', '>=', self.date_start)]
        if self.date_end:
            dom += [('date', '<=', self.date_end)]
        if self.as_of_date:
            dom += [('date', '<=', self.as_of_date)]
        res_ids = Result.search(dom)
        #self.results = Result.search(dom).sorted(
            #key=lambda l: (l.partner_id.search_key, l.date, l.move_id.name))
        res_ids = str(tuple(res_ids.ids))
        self._cr.execute("""
            select mol.id as move_line_id, mol.date as date, mol.date_maturity as date_maturity,
            mol.move_id as move_id, mol.partner_id as partner_id,
            mol.reconcile_id as reconcile_id, mol.currency_id as currency_id,
            mol.period_id as period_id,
            mol.document as document, mol.document_id as document_id
            from account_move_line mol
            left join account_move mov on mov.id = mol.move_id
            left join res_partner part on part.id = mol.partner_id
            left join account_move_reconcile mov_rec on mov_rec.id = mol.reconcile_id
            left join res_currency cur on cur.id = mol.currency_id
            where mol.id in """+(res_ids)+"""
            order by part.search_key, mol.date, mov.name
        """)

        results = self._cr.dictfetchall()
        ReportLine = self.env['xlsx.report.payable.detail.view']
        for line in results:
            mol = self.env["account.move.line"].browse(line['move_line_id'])
            mov = self.env["account.move"].browse(line['move_id'])
            if mol.invoice:
                tax_code = []
                sum_amount = []
                move_name = []
                transfer_type = []
                payment_export_name = []
                number_cheque = []
                income_tax = []
                payment_amount = []
                invoice = mol.invoice
                tax_code += [x.tax_code_id.code or False for x in invoice.tax_line]
                for payment_id in invoice.payment_ids:
                    if payment_id.move_id.doctype == "payment":
                        move_name += [payment_id.move_id.name or False]
                        payment_amount += [payment_id.document_id and payment_id.document_id._name == "account.voucher" and payment_id.document_id.amount or False]
                    if payment_id.move_id.doctype == "payment" and payment_id.move_id.document_id and payment_id.move_id.document_id._name == "account.voucher":
                        transfer_type += [(payment_id.move_id.document_id.payment_type == "transfer" and dict(self.env["account.voucher"]._columns["transfer_type"].selection)[payment_id.move_id.document_id.transfer_type] or "Cheque") or False]
                        payment_export_name += [payment_id.move_id.document_id.payment_export_id and payment_id.move_id.document_id.payment_export_id.state == "done" and payment_id.move_id.document_id.payment_export_id.name or False]
                        number_cheque += [payment_id.move_id.document_id.number_cheque or False]
                        income_tax += [payment_id.move_id.document_id.wht_cert_ids and dict(self.env["account.wht.cert"]._columns["income_tax_form"].selection)[payment_id.move_id.document_id.wht_cert_ids[0].income_tax_form] or False]
                        sum_amount += [payment_id.move_id.document_id.wht_cert_ids and sum(payment_id.move_id.document_id.wht_cert_ids[0].wht_line.filtered(lambda l: l.voucher_tax_id.invoice_id == invoice).mapped("amount")) or 0]
                        
                tax_code = ", ".join(list(filter(lambda l: l != False, tax_code)))
                move_name = ", ".join(list(filter(lambda l: l != False, move_name)))
                payment_amount = sum(list(filter(lambda l: l != False, payment_amount)))
                transfer_type = ", ".join(list(filter(lambda l: l != False, transfer_type)))
                payment_export_name = ", ".join(list(filter(lambda l: l != False, payment_export_name)))
                number_cheque = ", ".join(list(filter(lambda l: l != False, number_cheque)))
                income_tax = ", ".join(list(filter(lambda l: l != False, income_tax)))
                sum_amount = sum(list(filter(lambda l: l != False, sum_amount)))
                
            else:
                tax_code = None
                move_name = None
                payment_amount = None
                transfer_type = None
                payment_export_name = None
                number_cheque = None
                income_tax = None
                sum_amount = None
                
            line['tax_code'] = tax_code
            line['move_name'] = move_name
            line['payment_amount'] = payment_amount
            line['transfer_type'] = transfer_type
            line['payment_export_name'] = payment_export_name
            line['number_cheque'] = number_cheque
            line['income_tax'] = income_tax
            line['sum_amount'] = sum_amount
            
            self.results += ReportLine.new(line)
        return True



