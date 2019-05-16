# -*- coding: utf-8 -*-
from openerp import models, fields, api


class XLSXReportPurchaseInvoicePlan(models.TransientModel):
    _name = 'xlsx.report.purchase.invoice.plan'
    _inherit = 'report.account.common'
    
    
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    date_invoice_plan_start = fields.Date(
        string='Start Invoice Plan Date',
    )
    date_invoice_plan_end = fields.Date(
        string='End Invoice Plan Date',
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
            

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        
        Result = self.env['purchase.invoice.plan']
        dom = [('state','in',('paid','open'))]
        
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
        
        if self.date_invoice_plan_start:
            dom += [('order_id.date_order','>=',self.date_invoice_plan_start)]
        if self.date_invoice_plan_end:
            dom += [('order_id.date_order','<=',self.date_invoice_plan_end)]
        if self.date_contract_action_start:
            dom += [('order_id.contract_id.action_date','>=',self.date_contract_action_start)]
        if self.date_contract_action_end:
            dom += [('order_id.contract_id.action_date','<=',self.date_contract_action_end)]
        
        self.results = Result.search(dom)
        print '\n Result: '+str(self.results)







