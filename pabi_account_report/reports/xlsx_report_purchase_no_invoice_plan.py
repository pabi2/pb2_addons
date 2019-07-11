# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    inv_po_line = fields.Many2one(
        'purchase.order.line',
        string='PO line',
        compute='_compute_inv_po_line',
        readonly=True,
        store=False,
    )
    
    @api.multi
    def _compute_inv_po_line(self):
        for rec in self:
            if rec.purchase_line_id:
                rec.inv_po_line = rec.purchase_line_id.id
            else:
                search = rec.search([('invoice_id','=',rec.invoice_id.id),('purchase_line_id','!=',False)], limit=1)
                if search:
                    rec.inv_po_line = search.purchase_line_id.id
    


class XLSXReportPurchasenoInvoicePlan(models.TransientModel):
    _name = 'xlsx.report.purchase.no.invoice.plan'
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
    """po_name = fields.Char(
        string='Po Number',
        compute='_compute_po_name',
    )"""
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
        'account.invoice.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    """@api.multi
    @api.depends('purchase_ids')
    def _compute_po_name(self):
        for rec in self:
            if rec.purchase_ids:
                po_name = rec.purchase_ids.filtered('name').mapped('name')
                po_name = [x.strip() for x in po_name]
                po_name = ','.join(po_name)
                
                rec.po_name = str(po_name)
    """
    
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
    
    
    def get_domain_filter(self, fields, filters):
        dom = []
        n = 0
        codes = filters.replace(' ','').replace('\n',',').replace(',,',',').replace(',\n','').split(',')
        if '' in codes:
            codes.remove('')
        codes = [x.strip() for x in codes]
        for rec in codes:
            n += 1
            if rec != '':
                if n != len(codes):
                    dom.append('|')
                dom.append((fields, 'ilike', rec))
        return dom
    
    
    @api.onchange('line_po_filter')
    def _onchange_line_po_filter(self):
        self.purchase_ids = []
        Purchase = self.env['purchase.order']
        if self.line_po_filter:
            dom = self.get_domain_filter('name', self.line_po_filter)
            self.purchase_ids = Purchase.search(dom, order='id')
    
    @api.onchange('line_ct_filter')
    def _onchange_line_ct_filter(self):
        self.contract_ids = []
        Contract = self.env['purchase.contract']
        dom = []
        if self.line_ct_filter:
            dom = self.get_domain_filter('poc_code', self.line_ct_filter)
            self.contract_ids = Contract.search(dom, order='id')
    
    @api.onchange('line_acc_filter')
    def _onchange_line_acc_filter(self):
        self.account_ids = []
        Account = self.env['account.account']
        dom = []
        if self.line_acc_filter:
            dom = self.get_domain_filter('code', self.line_acc_filter)
            self.account_ids = Account.search(dom, order='id')
            

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        po_dom = []
        
        Result = self.env['account.invoice.line']
        dom = [('invoice_id','!=',False),('invoice_id.source_document_type','=','purchase'),
               ('invoice_id.state','!=','cancel'),('invoice_id.is_invoice_plan','!=',True),('invoice_id.source_document','like','PO')]
               #('inv_po_line.order_id.use_invoice_plan','!=',True)]
               #('invoice_id.source_document_id.use_invoice_plan','!=',True)]
               #('purchase_line_id.order_id.use_invoice_plan','!=',True)]
        
        if self.org_ids:
            #dom += [('inv_po_line.org_id', 'in', self.org_ids.ids)]
            #dom += [('invoice_id.source_document_id.org_id', 'in', self.org_ids.ids)]
            search = self.env['purchase.order'].search([('operating_unit_id.org_id', 'in', self.org_ids.ids)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.purchase_ids:
            #dom += [('inv_po_line.order_id', 'in', self.purchase_ids.ids)]\
            po_name = self.purchase_ids.filtered('name').mapped('name')
            #po_name = [x.strip() for x in po_name]
            #po_name = ','.join(po_name)
                
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.contract_ids:
            #dom += [('inv_po_line.order_id.contract_id', 'in', self.contract_ids.ids)]
            #dom += ['|',('order_id.contract_id', 'in', self.contract_ids.ids),('order_id.po_contract_type_id.contract_id', 'in', self.contract_ids.ids)]
            search = self.env['purchase.order'].search([('contract_id', 'in', self.contract_ids.ids)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.account_ids:
            #dom += [('inv_po_line.activity_rpt_id.account_id', 'in', self.account_ids.ids)]
            po_line = self.env['purchase.order.line'].search([('activity_rpt_id.account_id', 'in', self.account_ids.ids)])
            po_line = po_line.filtered('order_id')#.mapped('name')
            po_name = po_line.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.chartfield_ids:
            #dom += [('inv_po_line.chartfield_id', 'in', self.chartfield_ids.ids)]
            dom += [('chartfield_id', 'in', self.chartfield_ids.ids)]
        
        if self.date_po_start and not self.date_po_end:
            #dom += [('order_id.date_order','>=',self.date_po_start)]
            search = self.env['purchase.order'].search([('date_order', '=', self.date_po_start)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.date_po_start and self.date_po_end:
            #dom += [('order_id.date_order','<=',self.date_po_end)]
            search = self.env['purchase.order'].search([('date_order', '>=', self.date_po_start),('date_order','<=',self.date_po_end)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.date_start:
            dom += [('invoice_id.date_document','>=',self.date_start)]
        if self.date_end:
            dom += [('invoice_id.date_document','<=',self.date_end)]
        if self.period_start_id:
            #dom += [('inv_po_line.order_id.date_order','>=',self.period_start_id.date_start)]
            search = self.env['purchase.order'].search([('date_order','>=',self.period_start_id.date_start)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.period_end_id:
            #dom += [('inv_po_line.order_id.date_order','<=',self.period_end_id.date_stop)]
            search = self.env['purchase.order'].search([('date_order','<=',self.period_end_id.date_stop)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.date_contract_action_start:
            #dom += [('inv_po_line.order_id.contract_id.action_date','>=',self.date_contract_action_start)]
            search = self.env['purchase.order'].search([('contract_id.action_date','>=',self.date_contract_action_start)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        if self.date_contract_action_end:
            #dom += [('inv_po_line.order_id.contract_id.action_date','<=',self.date_contract_action_end)]
            search = self.env['purchase.order'].search([('contract_id.action_date','<=',self.date_contract_action_end)])
            po_name = search.filtered('name').mapped('name')
            
            dom += [('invoice_id.source_document','in',po_name)]
            
        print 'Dom: '+str(dom)
        
        #self.results = Result.search(dom, order="inv_po_line.org_id,inv_po_line.fiscalyear_id.name,inv_po_line.order_id.date_order,inv_po_line.order_id.name,inv_po_line.docline_seq")
        self.results = Result.search(dom)
        print '\n Result: '+str(self.results)
        
        