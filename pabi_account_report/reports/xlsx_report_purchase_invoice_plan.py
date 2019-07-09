# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportPurchaseInvoicePlan(models.TransientModel):
    _name = 'xlsx.report.purchase.invoice.plan'
    _inherit = 'report.account.common'
    
    
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_no',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    date_po_start = fields.Date(
        string='Start PO Date',
    )
    date_po_end = fields.Date(
        string='End PO Date',
    )
    purchase_ids = fields.Many2many(
        'purchase.order',
        string='Po Number',
    )
    contract_ids = fields.Many2many(
        'purchase.contract',
        string='Po Contract',
    )
    date_contract_action_start = fields.Date(
        string='Start Contract Action Date',
    )
    date_contract_action_end = fields.Date(
        string='End Contract Action Date',
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Account',
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    line_po_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    line_ct_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    line_acc_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    results = fields.Many2many(
        'purchase.invoice.plan',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
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
    
    @api.onchange('line_po_filter')
    def _onchange_line_po_filter(self):
        self.purchase_ids = []
        Purchase = self.env['purchase.order']
        dom = []
        if self.line_po_filter:
            codes = self.line_po_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('name', 'ilike', codes))
            self.purchase_ids = Purchase.search(dom, order='id')
    
    @api.onchange('line_ct_filter')
    def _onchange_line_ct_filter(self):
        self.contract_ids = []
        Contract = self.env['purchase.contract']
        dom = []
        if self.line_ct_filter:
            codes = self.line_ct_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('poc_code', 'ilike', codes))
            self.contract_ids = Contract.search(dom, order='id')
    
    @api.onchange('line_acc_filter')
    def _onchange_line_acc_filter(self):
        self.account_ids = []
        Account = self.env['account.account']
        dom = []
        if self.line_acc_filter:
            codes = self.line_acc_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.account_ids = Account.search(dom, order='id')
            

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        
        Result = self.env['purchase.invoice.plan']
        dom = [('order_id.state','!=','cancel'),('order_id.order_type','=','purchase_order')]
        
        if self.org_ids:
            dom += [('order_line_id.org_id', 'in', self.org_ids.ids)]
        if self.purchase_ids:
            dom += [('order_id', 'in', self.purchase_ids.ids)]
        if self.contract_ids:
            dom += [('order_id.contract_id', 'in', self.contract_ids.ids)]
            #dom += ['|',('order_id.contract_id', 'in', self.contract_ids.ids),('order_id.po_contract_type_id.contract_id', 'in', self.contract_ids.ids)]
        if self.account_ids:
            dom += [('order_line_id.activity_rpt_id.account_id', 'in', self.account_ids.ids)]
        if self.chartfield_ids:
            dom += [('order_line_id.chartfield_id', 'in', self.chartfield_ids.ids)]
        
        if self.date_po_start and not self.date_po_end:
            dom += [('order_id.date_order','=',self.date_po_start)]
        if self.date_po_start and self.date_po_end:
            dom += [('order_id.date_order','>=',self.date_po_start),('order_id.date_order','<=',self.date_po_end)]
        if self.date_start:
            dom += [('order_id.date_order','>=',self.date_start)]
        if self.date_end:
            dom += [('order_id.date_order','<=',self.date_end)]
        if self.period_start_id:
            dom += [('order_id.date_order','>=',self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('order_id.date_order','<=',self.period_end_id.date_stop)]
        if self.date_contract_action_start:
            dom += [('order_id.contract_id.action_date','>=',self.date_contract_action_start)]
        if self.date_contract_action_end:
            dom += [('order_id.contract_id.action_date','<=',self.date_contract_action_end)]
        
        self.results = Result.search(dom)
        print '\n Result: '+str(self.results)
        