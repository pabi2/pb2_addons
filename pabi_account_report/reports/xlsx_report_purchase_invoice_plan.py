# -*- coding: utf-8 -*-
from openerp import models, fields, api
from Scripts.runxlrd import result


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
    
    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        where_str = 'and'.join(where_dom)
        where_str = where_str.replace(',)',')')
        return where_str
    
    
    @api.multi
    def get_model_chartfield(self):
        section = project = asset = phase = personnel = []
        result = []
        """model = [('res.section', 'section'),
                 ('res.project', 'project'),
                 ('res.invest.asset', 'asset'),
                 ('res.invest.construction.phase', 'phase'),
                 ('res.personnel.costcenter', 'personnel')]"""
        for chartfield in self.chartfield_ids:
            #result[model[chartfield.model]].append(chartfield.res_id)
            
            if chartfield.model == 'res.section':
                section.append(chartfield.res_id)
            if chartfield.model == 'res.project':
                project.append(chartfield.res_id)
            if chartfield.model == 'res.invest.asset':
                asset.append(chartfield.res_id)
            if chartfield.model == 'res.invest.construction.phase':
                phase.append(chartfield.res_id)
            if chartfield.model == 'res.personnel.costcenter':
                personnel.append(chartfield.res_id)
        
        result.append(('section',section))
        result.append(('project',project))
        result.append(('asset',asset))
        result.append(('phase',phase))
        result.append(('personnel',personnel))
        
        print 'Result: '+str(result)
        return result
    
    
    @api.multi
    def get_array_list(self, ids):
        arr = []
        tt = ''
        for id in ids:
            arr.append(id)
        ids = str(ids).replace('[','').replace(']','')
        ids = ids.split(',')
        codes = [x.strip() for x in ids]
        codes = tuple(codes)
        return codes
    
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        ids = []
        InvoicePlan = self.env['purchase.invoice.plan']
        dom = [('po.state','!=','cancel'),('po.order_type','=','purchase_order')]
        
        if self.org_ids:
            dom += [('org.id', 'in', self.get_array_list(self.org_ids.ids))]
        if self.purchase_ids:
            dom += [('po.id', 'in', self.get_array_list(self.purchase_ids.ids))]
        if self.contract_ids:
            dom += [('pct.id', 'in', self.get_array_list(self.contract_ids.ids))]
            #dom += ['|',('order_id.contract_id', 'in', self.contract_ids.ids),('order_id.po_contract_type_id.contract_id', 'in', self.contract_ids.ids)]
        if self.account_ids:
            dom += [('rpt.account_id', 'in', self.get_array_list(self.account_ids.ids))]
        if self.chartfield_ids:
            dom += [('pol.chartfield_id', 'in', self.get_array_list(self.chartfield_ids.ids))]
        
        if self.date_po_start and not self.date_po_end:
            dom += [('po.date_order','=',self.date_po_start)]
        if self.date_po_start and self.date_po_end:
            dom += [('po.date_order','>=',self.date_po_start),('po.date_order','<=',self.date_po_end)]
        if self.date_start:
            dom += [('po.date_order','>=',self.date_start)]
        if self.date_end:
            dom += [('po.date_order','<=',self.date_end)]
        if self.period_start_id:
            dom += [('po.date_order','>=',self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('po.date_order','<=',self.period_end_id.date_stop)]
        if self.date_contract_action_start:
            dom += [('pct.action_date','>=',self.date_contract_action_start)]
        if self.date_contract_action_end:
            dom += [('pct.action_date','<=',self.date_contract_action_end)]
        
        self.get_model_chartfield()
        
        where_str = self._domain_to_where_str(dom)
        print 'WHERE: '+where_str
        self._cr.execute("""
            select
                pip.id
            from purchase_invoice_plan pip
                left join purchase_order_line pol on pol.id = pip.order_line_id
                left join purchase_order po on po.id = pip.order_id
                left join res_org org on org.id = pol.org_id
                left join purchase_contract pct on pct.id = po.contract_id
                left join account_activity rpt on rpt.id = pol.activity_rpt_id
            where 
        """  + where_str + ' order by org.name, pol.fiscalyear_id, po.date_order, po.name, pol.docline_seq ' )
        
        #order.state != 'cancel' and order.order_type = 'purchase_order' and order_id in [8316] 
        
        invoice_plans = self._cr.dictfetchall()
        
        """for plan in invoice_plans:
            ids.append(plan['id'])
        results = InvoicePlan.browse(ids)
        print 'results2: '+str(results)"""
        
        self.results = results
        
        
        
        
        
        #self.results = Result.search(dom, order="order_line_id.org_id,order_line_id.fiscalyear_id.name,order_id.date_order,order_id.name,order_line_id.docline_seq")
        #self.results = Result.search(dom)
        #print '\n Result: '+str(self.results)
        
        