# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    budget_fund_rule_line_id = fields.Many2one(
        'budget.fund.rule.line',
        string='Budget Fund Rule Line',
        compute='_compute_budget_fund_rule_line',
    )
    tax_code = fields.Char(
        string='Tax',
        compute='_compute_tax',
    )
    vat_amount = fields.Float(
        string = 'VAT Amount',
        compute='_compute_vat_amount',
    )
    base_amount = fields.Float(
        string = 'Base Amount',
         compute='_compute_base_amount',
    )

    @api.multi
    def _compute_tax(self):
        for move in self:
            if move.doctype == 'interface_account': 
                Fund = self.env['interface.account.entry'] 
                domain = ([('move_id', '=', move.move_id.id)])
                lines = Fund.search(domain)
                tax = []
                if lines.line_ids:
                    for line in lines.line_ids:
                        if line.tax_id.id:
                            tax.append(line.tax_id.description)
                    move.tax_code = ", ".join(tax)  
            else:
                tax = []
                if move.move_id.invoice_ids:
                    for line_invoice in move.move_id.invoice_ids.invoice_line:
                        for tax_line in line_invoice.invoice_line_tax_id:
                            for tax_code in tax_line:
                                tax.append(tax_code.description)
                    move.tax_code = ", ".join(list(dict.fromkeys(tax)))               
    
    @api.multi
    def _compute_vat_amount(self):
        for move in self:
            if move.doctype == 'interface_account': 
                Fund = self.env['interface.account.entry'] 
                domain = ([('move_id', '=', move.move_id.id)])
                lines = Fund.search(domain)
                for line in lines.line_ids:
                    if line.tax_id.id:
                        move.vat_amount = line.credit
            elif move.doctype == 'out_invoice' or move.doctype == 'in_invoice' : 
                Fund = self.env['account.invoice'] 
                domain = ([('move_id', '=', move.move_id.id)])
                lines = Fund.search(domain)
                for line in lines.invoice_line:
                    if line.invoice_line_tax_id:
                        move.vat_amount = lines.amount_tax
                        
            else: #1080789
                #move.vat_amount = abs(sum(move.move_id.invoice_ids.tax_line.mapped("amount")))
                if move.move_id.tax_detail_ids:
                    move.vat_amount = abs(sum(move.move_id.tax_detail_ids.mapped("amount")))
                
    @api.multi
    def _compute_base_amount(self):
        for move in self:
            if move.doctype == 'interface_account': 
                Fund = self.env['interface.account.entry'] 
                domain = ([('move_id', '=', move.move_id.id)])
                lines = Fund.search(domain)
                for line in lines.line_ids:
                    if line.tax_id.id:
                        move.base_amount = line.tax_base_amount
            elif move.doctype == 'out_invoice' or move.doctype == 'in_invoice' : 
                Fund = self.env['account.invoice'] 
                domain = ([('move_id', '=', move.move_id.id)])
                lines = Fund.search(domain)
                for line in lines.invoice_line:
                    if line.invoice_line_tax_id:
                        move.base_amount = lines.amount_untaxed
            else:
                if move.move_id.tax_detail_ids:
                    move.base_amount = abs(sum(move.move_id.tax_detail_ids.mapped("base")))
                #move.base_amount = abs(sum(move.move_id.invoice_ids.tax_line.mapped("base"))) 
                             
    @api.multi
    def _compute_budget_fund_rule_line(self):
        for rec in self:
            Fund = self.env['budget.fund.rule.line']
            domain = ([('fund_rule_id.fund_id', '=', rec.fund_id.id),
                       ('fund_rule_id.project_id', '=', rec.project_id.id),
                       ('fund_rule_id.state', '=', 'confirmed'),
                       ('account_ids', 'in', rec.account_id.id)])
            lines = Fund.search(domain)
            if len(lines) > 1:
                rec.budget_fund_rule_line_id = lines[0]
            rec.budget_fund_rule_line_id = lines


class XLSXReportGlProject(models.TransientModel):
    _name = 'xlsx.report.gl.project'
    _inherit = 'report.account.common'

    account_type_id = fields.Many2one(
        'account.account.type',
        string='Account Type',
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Account Code',
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=['|',('active', '=', False),('active', '=', True),('model', '!=', 'res.personnel.costcenter')],
    )
    chart_view = fields.Selection(
        [('personnel', 'Personnel'),
         ('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
        required=False,
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    invest_asset_ids = fields.Many2many(
        'res.invest.asset',
        string='Investment Asset',
    )
    section_ids = fields.Many2many(
        'res.section',
        string='Section',
    )
    fund_ids = fields.Many2many(
        'res.fund',
        string='Source of Fund',
    )
    project_ids = fields.Many2many(
        'res.project',
        string='Project',
    )
    invest_construction_ids = fields.Many2many(
        'res.invest.construction',
        string='Project (C)',
    )
    activity_group_ids = fields.Many2many(
        'account.activity.group',
        string='Activity Group',
    )
    activity_ids = fields.Many2many(
        'account.activity',
        string='Activity',
    )
    count_chartfield = fields.Integer(
        compute='_compute_count_chartfield',
        string='Budget Count',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    filter = fields.Selection(
        selection_add=[('filter_clearing_date', 'Clearing date')],
    )
    cleaning_date_start = fields.Date(
        string='Start Date',
    )
    cleaning_date_end = fields.Date(
        string='End Date',
    )
    line_filter_job = fields.Text(
        string='Job',
        help="More filter Job. You can use complex search with comma and between.",
    )

    job_order_ids = fields.Many2many(
        'cost.control',
        string='Job Order',
    )
    count_job_order = fields.Integer(
        compute='_compute_job_order',
        string='Job Order Count',
    )

    @api.onchange('chart_view')
    def _onchange_chart_view(self):
        self.org_ids = False
        self.invest_asset_ids = False
        self.section_ids = False
        self.fund_ids = False
        self.project_ids = False
        self.invest_construction_ids = False

    @api.multi
    @api.depends('chartfield_ids')
    def _compute_count_chartfield(self):
        for rec in self:
            rec.count_chartfield = len(rec.chartfield_ids)
            
    @api.multi
    @api.depends('job_order_ids')
    def _compute_job_order(self):
        for rec in self:
            rec.count_job_order = len(rec.job_order_ids)

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = []
        if self.account_type_id:
            dom += [('account_id.user_type', '=', self.account_type_id.id)]
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.activity_group_ids:
            dom += [('activity_group_id', 'in', self.activity_group_ids.ids)]
        if self.activity_ids:
            dom += [('activity_id', 'in', self.activity_ids.ids)]
        if self.charge_type:
            dom += [('charge_type', '=', self.charge_type)]
        # Filter chart view
        if self.chart_view == 'personnel':
            dom += [('org_id', '!=', False)]
        elif self.chart_view == 'invest_asset':
            dom += [('invest_asset_id', '!=', False)]
        elif self.chart_view == 'unit_base':
            dom += [('section_id', '!=', False)]
        elif self.chart_view == 'project_base':
            dom += [('project_id', '!=', False)]
        elif self.chart_view == 'invest_construction':
            dom += [('invest_construction_id', '!=', False)]
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids.ids)]
        if self.invest_asset_ids:
            dom += [('invest_asset_id', 'in', self.invest_asset_ids.ids)]
        if self.section_ids:
            dom += [('section_id', 'in', self.section_ids.ids)]
        if self.fund_ids:
            dom += [('fund_id', 'in', self.fund_ids.ids)]
        if self.project_ids:
            dom += [('project_id', 'in', self.project_ids.ids)]
        if self.invest_construction_ids:
            dom += [('invest_construction_id', 'in',
                     self.invest_construction_ids.ids)]
            
        if self.job_order_ids:
            dom += [('cost_control_id', 'in', self.job_order_ids.ids)]
            
        if self.chartfield_ids:
            # map beetween chartfield_id with chartfield type
            chartfields = [('section_id', 'sc:'),
                           ('project_id', 'pj:'),
                           ('invest_construction_phase_id', 'cp:'),
                           ('invest_asset_id', 'ia:'),
                           ('personnel_costcenter_id', 'pc:')]
            where_str = ''
            res_ids = []
            for chartfield_id, chartfield_type in chartfields:
                chartfield_ids = self.chartfield_ids.filtered(
                    lambda l: l.type == chartfield_type).mapped('res_id')
                if chartfield_ids:
                    if where_str:
                        where_str += ' or '
                    where_str += chartfield_id + ' in %s'
                    res_ids.append(tuple(chartfield_ids))
            if res_ids:
                sql = "select id from account_move_line where " + where_str
                self._cr.execute(sql, res_ids)
                dom += [('id', 'in', map(lambda l: l[0], self._cr.fetchall()))]
        # Filter date
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
        if self.cleaning_date_start and self.cleaning_date_end:
            check=Result.with_context(active=False).search(dom)
            cleaning_ids = []
            for record in check:
                if record.charge_type == "external":
                    if record.document_id!=False and record.document_id._name != "stock.picking":
                        try:
                            _check= ", ".join(list(filter(lambda l: l != False, [x.move_id.document_id and "bank_receipt_id" in x.move_id.document_id._columns.keys() and x.move_id.document_id.bank_receipt_id.move_id.date or False for x in record.document_id.payment_ids])))
                            if record.document_id.type not in ("out_invoice", "out_refund"):
                                pay_date = ", ".join(list(filter(lambda l: l != False, [x.move_id.doctype == "payment" and x.move_id.date or False for x in record.document_id.payment_ids])))
                            if not(record.document_id._name == "account.invoice" and record.id != record.document_id.cancel_move_id.id):
                                pay_date = ", ".join([x.move_id.date for x in self.env["interface.account.entry"].search([("number", "=", record.document_id.to_payment)]).move_id.line_id.mapped("bank_receipt_id")])
                        except Exception:
                            if _check and datetime.datetime.strptime(self.cleaning_date_start, "%Y-%m-%d").date() <=  datetime.datetime.strptime(_check, "%Y-%m-%d").date() <= datetime.datetime.strptime(self.cleaning_date_end, "%Y-%m-%d").date(): 
                                cleaning_ids.append(record.id)
                            pass    
                        if pay_date and datetime.datetime.strptime(self.cleaning_date_start, "%Y-%m-%d").date() <=  datetime.datetime.strptime(pay_date, "%Y-%m-%d").date() <= datetime.datetime.strptime(self.cleaning_date_end, "%Y-%m-%d").date():
                            cleaning_ids.append(record.id)
                        if _check and (not pay_date) and datetime.datetime.strptime(self.cleaning_date_start, "%Y-%m-%d").date() <=  datetime.datetime.strptime(_check, "%Y-%m-%d").date() <= datetime.datetime.strptime(self.cleaning_date_end, "%Y-%m-%d").date():
                            cleaning_ids.append(record.id)
                else:
                    cleaning_ids.append(record.id)
            self.results = Result.search([['id','in',cleaning_ids]])
        else:
            self.results = Result.with_context(active=False).search(dom)

    @api.onchange('line_filter')
    def _onchange_line_filter(self):
        self.chartfield_ids = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.line_filter:
            codes = self.line_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.chartfield_ids = Chartfield.search(dom, order='id')
            
    @api.onchange('line_filter_job')
    def _onchange_line_filter_job(self):
        self.job_order_ids = []
        Cost = self.env['cost.control']
        dom = []
        n=0
        if self.line_filter_job:
            codes = self.line_filter_job.replace(' ','').replace('\n',',').replace(',,',',').replace(',\n','').split(',')
            if '' in codes:
                codes.remove('')
            codes = [x.strip() for x in codes]
            for rec in codes:
                n += 1
                if rec != '':
                    if n != len(codes):
                        dom.append('|')
                    dom.append(('code', 'ilike', rec))
            self.job_order_ids = Cost.search(dom, order='id')

    @api.onchange('account_type_id')
    def _onchange_account_type(self):
        self.account_ids = False
        account_type_id = self.account_type_id.id
        domain = [('type', '!=', 'view')]
        if account_type_id:
            domain = [('user_type', '=', account_type_id)]
        return {'domain': {'account_ids': domain}}