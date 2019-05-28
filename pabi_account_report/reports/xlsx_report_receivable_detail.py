# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime
import time
import pandas as pd
import re


class XLSXReportReceivableDetailView(models.AbstractModel):
    _name = 'xlsx.report.receivable.detail.view'
    _inherit = 'account.move.line'

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
    )
    move_name = fields.Text(
        string='Move Name',
    )
    move_date = fields.Date(
        string='Move Date',
    )
    number_preprint = fields.Text(
        string='Preprint Number',
    )
    amount_preprint = fields.Float(
        string='Preprint Amount',
    )

    
    

class XLSXReportReceivableDetail(models.TransientModel):
    _name = 'xlsx.report.receivable.detail'
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
    system_ids = fields.Many2many(
        'interface.system',
        string='System Origin',
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
        'xlsx.report.receivable.detail.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.onchange('filter')
    def _onchange_filter(self):
        super(XLSXReportReceivableDetail, self)._onchange_filter()
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
        Moveline = self.env['account.move.line']
        dom = [('account_id.type', '=', 'receivable'),
               ('move_id.state', '=', 'posted'),]
               #('date_maturity', '!=', False),]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.move_ids:
            dom += [('move_id', 'in', self.move_ids.ids)]
        if self.system_ids:
            dom += [('system_id', 'in', self.system_ids.ids)]
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
        res_ids = []
        for x in Moveline.search(dom):
            res_ids += [x.id if x.move_id.doctype == 'adjustment' or x.date_maturity else False]
        res_ids = list(filter(lambda l: l != False, res_ids))
        #self.results = Result.search(res).sorted(
        #    key=lambda l: (l.partner_id.search_key, l.date, l.move_id.name))
        res_ids = str(tuple(res_ids))
        self._cr.execute("""
            select mol.id as move_line_id, mol.date as date, mol.date_maturity as date_maturity,
            mol.move_id as move_id, mol.partner_id as partner_id,
            mol.reconcile_id as reconcile_id, mol.currency_id as currency_id,
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
        ReportLine = self.env['xlsx.report.receivable.detail.view']
        for line in results:
            mol = self.env["account.move.line"].browse(line['move_line_id'])
            mov = self.env["account.move"].browse(line['move_id'])
            if mov.document_id and mov.document_id._name == "account.invoice" and mov.id != mov.document_id.cancel_move_id.id:
                move_name = []
                move_date = []
                number_preprint = []
                amount_preprint = []
                payment_ids = mov.document_id.payment_ids       
                for payment in payment_ids:
                    move_name += [payment.move_id.doctype == "receipt" and payment.move_id.name or False]
                    move_date += [payment.move_id.doctype == "receipt" and payment.move_id.date or False]
                    number_preprint += [payment.move_id.doctype == "receipt" and payment.move_id.document_id._name == "account.voucher" and payment.move_id.document_id.number_preprint or False]
                    amount_preprint += [payment.move_id.doctype == "receipt" and payment.move_id.document_id._name == "account.voucher" and payment.document_id.amount or 0]
                    
                move_name = ", ".join(list(filter(lambda l: l != False, move_name)))
                move_date = ", ".join(list(filter(lambda l: l != False, move_date)))
                number_preprint = ", ".join(list(filter(lambda l: l != False, number_preprint)))
                amount_preprint = sum(list(filter(lambda l: l != False, amount_preprint)))
            
            elif mov.document_id and mov.document_id._name == "interface.account.entry":
                search_line = self.env["interface.account.entry"].search([("number", "=", mov.document_id.to_payment)]).line_ids.filtered(lambda l: l.account_id.code == mol.account_id.code and l.name == mol.name and l.id != mol.id)
                move_name = mov.document_id.to_payment
                move_date = self.env["interface.account.entry"].search([("number", "=", mov.document_id.to_payment)]).move_id.date
                number_preprint = self.env["interface.account.entry"].search([("number", "=", mov.document_id.to_payment)]).preprint_number
                amount_preprint = sum(search_line.mapped("credit")) - sum(search_line.mapped("debit"))
            else:
                move_name = None
                move_date = None
                number_preprint = None
                amount_preprint = None
            
            line['move_name'] = move_name
            line['move_date'] = move_date
            line['number_preprint'] = number_preprint
            line['amount_preprint'] = amount_preprint
            
            self.results += ReportLine.new(line)
        return True


        
        
        

        
