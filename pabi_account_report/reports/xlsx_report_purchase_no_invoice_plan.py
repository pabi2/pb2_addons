# -*- coding: utf-8 -*-
from openerp import models, fields, api


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
        'report.purchase.no.invoice.plan.view',
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
        result = section = project = asset = phase = personnel = []
        
        for chartfield in self.chartfield_ids:
            if chartfield.model == 'res.section':
                section.append(chartfield.res_id)
            elif chartfield.model == 'res.project':
                project.append(chartfield.res_id)
            elif chartfield.model == 'res.invest.asset':
                asset.append(chartfield.res_id)
            elif chartfield.model == 'res.invest.construction.phase':
                phase.append(chartfield.res_id)
            elif chartfield.model == 'res.personnel.costcenter':
                personnel.append(chartfield.res_id)
        
        return {
                'section': section,
                'project': project,
                'asset': asset,
                'phase': phase,
                'personnel': personnel
            }
    
    @api.multi
    def get_where_str_chartfield(self):
        dom = []
        chartfield_dom = []
        
        chartfield = self.get_model_chartfield()
        if chartfield['section']:
            chartfield_dom += [('pol.section_id','in',tuple(chartfield['section']))]
        if chartfield['project']:
            chartfield_dom += [('pol.project_id','in',tuple(chartfield['project']))]
        if chartfield['asset']:
            chartfield_dom += [('pol.invest_asset_id','in',tuple(chartfield['asset']))]
        if chartfield['phase']:
            chartfield_dom += [('pol.invest_construction_phase_id','in',tuple(chartfield['phase']))]
        if chartfield['personnel']:
            chartfield_dom += [('pol.personnel_costcenter_id','in',tuple(chartfield['personnel']))]
            
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in chartfield_dom]
        
        where_str = 'or'.join(where_dom)
        where_str = 'and (' + where_str.replace(',)',')') + ') '
        return where_str
    

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        line_ids = []
        chartfield_dom = ''
        
        InvoiceLine = self.env['account.invoice.line']
        Reports = self.env['report.purchase.no.invoice.plan.view']
        
        dom = [('av.source_document_type','=','purchase'),('av.state','!=','cancel'),('av.is_invoice_plan','!=',True),('po.order_type','=','purchase_order')]
        
        if self.org_ids:
            dom += [('org.id','in',tuple(self.org_ids.ids))]
            
        if self.purchase_ids:
            dom += [('po.id','in',tuple(self.purchase_ids.ids))]
            
        if self.contract_ids:
            dom += [('po.contract_id', 'in', tuple(self.contract_ids.ids))]
            
        if self.account_ids:
            dom += [('rpt.account_id', 'in', tuple(self.account_ids.ids))]
            
        if self.chartfield_ids:
            chartfield_dom = self.get_where_str_chartfield()
        
        if self.date_po_start and not self.date_po_end:
            dom += [('cast(po.date_order as date)', '=', self.date_po_start)]
            
        if self.date_po_start and self.date_po_end:
            dom += [('cast(po.date_order as date)', '>=', self.date_po_start),('cast(po.date_order as date)','<=',self.date_po_end)]
            
        if self.date_start:
            dom += [('av.date_document','>=',self.date_start)]
        if self.date_end:
            dom += [('av.date_document','<=',self.date_end)]
        if self.period_start_id:
            dom += [('cast(po.date_order as date)','>=',self.period_start_id.date_start)]
            
        if self.period_end_id:
            dom += [('cast(po.date_order as date)','<=',self.period_end_id.date_stop)]
            
        if self.date_contract_action_start:
            dom += [('pct.action_date','>=',self.date_contract_action_start)]
            
        if self.date_contract_action_end:
            dom += [('pct.action_date','<=',self.date_contract_action_end)]
        
        where_str = self._domain_to_where_str(dom)
        where_str += chartfield_dom
        
        self._cr.execute("""
            select 
                pol.org_id as purchase_id, po.id as purchase_id, pct.id as contract_id, aa.id as account_id,
                ou.name as org, fis.name as po_fiscalyear, 
                cast(po.date_order as date) as po_order_date, 
                po.name as po_number, pol.docline_seq as item,
                case
                    when po.contract_id is not null then pct_t.name
                    when po.po_contract_type_id is not null then po_pct_t.name
                    else ''
                end as po_contract_type,
                pct.id as contract_id,
                org.id as org_id,
                po.id as purchase_id,
                rpt.id as account_id,
                pct.action_date as contract_action_date,
                to_char(po.date_contract_start, 'DD/MM/YYYY') as contract_start_date, 
                to_char(po.date_contract_end, 'DD/MM/YYYY') as contract_end_date, 
                part.search_key as supplier_code, part.name as supplier_name, pro_cate.name as product_cat, 
                prod.name_template as product_name, pol.name as description, ag.name as activity_group, 
                rpt.name as activity_rpt, aa.code as account_code, aa.name as account_name, 
                case
                    when pol.section_id is not null then sec.code
                    when pol.project_id is not null then prj.code
                    when pol.invest_asset_id is not null then asset.code
                    when pol.invest_construction_phase_id is not null then phase.code
                    when pol.personnel_costcenter_id is not null then rpc.code
                    else ''
                end as budget_code,
                case
                    when pol.section_id is not null then sec.name
                    when pol.project_id is not null then prj.name
                    when pol.invest_asset_id is not null then asset.name
                    when pol.invest_construction_phase_id is not null then phase.name
                    when pol.personnel_costcenter_id is not null then rpc.name
                    else ''
                end as budget_name,
                fund.name as fund, '' as fiscal_year_by_invoice_plan, ROUND(pol.product_qty,2) as product_qty, 
                pol.price_unit as unit_price, '' as installment, avl.name as inv_plan_description, 
                '' as invoice_date, '' as advance, '' as deposit_percent, avl.price_subtotal as plan_amount, cur.name as currency, 
                '' as invoice_percent, 
                (SELECT STRING_AGG(tax.description, ', ') AS state_code 
                 FROM account_tax tax 
                     LEFT JOIN purchase_order_taxe pot ON pot.tax_id = tax.id
                 WHERE pot.ord_id = pol.id
                ) AS taxes,
                avl.price_subtotal as plan_subtotal,
                av.state as status, 
                (select wa.name from purchase_work_acceptance_line wal 
                     left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.supplier_invoice = av.supplier_invoice_number limit 1
                ) as wa_number,
                (select wal.to_receive_qty from purchase_work_acceptance_line wal 
                     left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.supplier_invoice = av.supplier_invoice_number limit 1
                ) as plan_qty,
                (select wal.price_unit_untaxed from purchase_work_acceptance_line wal 
                     left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.supplier_invoice = av.supplier_invoice_number limit 1
                ) as plan_unit_price,
                (select wal.price_subtotal from purchase_work_acceptance_line wal 
                     left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.supplier_invoice = av.supplier_invoice_number limit 1
                ) as subtotal,
                pbil.name as billing_number, av.number as kv_number, to_char(av.date_document, 'DD/MM/YYYY') as date_document, 
                to_char(av.date_invoice, 'DD/MM/YYYY') as posting_date, av.supplier_invoice_number,
                avl.price_subtotal as inv_amount,
                po.use_deposit as deposit, 
                ads.name as advance_deposit, 
                po.is_fin_lease as fin_lease
            from account_invoice_line avl
                left join account_invoice av on av.id = avl.invoice_id
                left join purchase_order_line pol on pol.id = avl.purchase_line_id
                left join purchase_order po on po.id = pol.order_id
                left join account_fiscalyear fis on fis.id = pol.fiscalyear_id
                left join res_org org on org.id = pol.org_id
                left join operating_unit ou on ou.id = org.operating_unit_id
                left join purchase_contract pct on pct.id = po.contract_id
                left join purchase_contract_type pct_t on pct_t.id = pct.contract_type_id
                left join purchase_contract_type po_pct_t on po_pct_t.id = po.po_contract_type_id
                left join account_activity_group ag on ag.id = pol.activity_group_id
                left join account_activity rpt on rpt.id = pol.activity_rpt_id
                left join account_account aa on aa.id = rpt.account_id
                left join res_partner part on part.id = po.partner_id
                left join product_product prod on prod.id = pol.product_id
                left join product_template prot on prot.id = prod.product_tmpl_id
                left join product_category pro_cate on pro_cate.id = prot.categ_id
                left join res_fund fund on fund.id = pol.fund_id
                left join res_section sec on sec.id = pol.section_id
                left join res_project prj on prj.id = pol.project_id
                left join res_invest_asset asset on asset.id = pol.invest_asset_id
                left join res_invest_construction_phase phase on phase.id = pol.invest_construction_phase_id
                left join res_personnel_costcenter rpc on rpc.id = pol.personnel_costcenter_id
                left join purchase_billing pbil on pbil.id = av.purchase_billing_id
                left join res_currency cur on cur.id = po.currency_id
                left join account_account ads on ads.id = po.account_deposit_supplier
            where
        """  + where_str + ' order by ou.name, pol.fiscalyear_id, po.date_order, po.name, pol.docline_seq')
        #search = rec.search([('invoice_id','=',rec.invoice_id.id),('purchase_line_id','!=',False)], limit=1)
        
        invoice_lines = self._cr.dictfetchall()
        
        for line in invoice_lines:
            self.results += Reports.new(line)
        
        print 'results: '+str(self.results)


class ReportPurchaseNoInvoicePlanView(models.AbstractModel):
    _name = 'report.purchase.no.invoice.plan.view'
    #_auto = False
    
    #id = fields.Integer()
    org_id = fields.Many2one('res.org')
    purchase_id = fields.Many2one('purchase.order')
    contract_id = fields.Many2one('purchase.contract')
    account_id = fields.Many2one('account.account')
    
    org = fields.Char()
    po_fiscalyear = fields.Char()
    po_order_date = fields.Date()
    po_number = fields.Char()
    item = fields.Char()
    po_contract_type = fields.Char()
    contract_action_date = fields.Date()
    contract_start_date = fields.Char()
    contract_end_date = fields.Char()
    supplier_code = fields.Char()
    supplier_name = fields.Char()
    product_cat = fields.Char()
    product_name = fields.Char()
    description = fields.Char()
    activity_group = fields.Char()
    activity_rpt = fields.Char()
    account_code = fields.Char()
    account_name = fields.Char()
    budget_code = fields.Char()
    budget_name = fields.Char()
    fund = fields.Char()
    fiscal_year_by_invoice_plan = fields.Char()
    quantity = fields.Char()
    unit_price = fields.Char()
    installment = fields.Char()
    inv_plan_description = fields.Char()
    invoice_date = fields.Char()
    advance = fields.Char()
    deposit_percent = fields.Char()
    plan_amount = fields.Char()
    currency = fields.Char()
    invoice_percent = fields.Char()
    taxes = fields.Char()
    plan_subtotal = fields.Char()
    status = fields.Char()
    wa_number = fields.Char()
    plan_qty = fields.Char()
    plan_unit_price = fields.Char()
    subtotal = fields.Char()
    billing_number = fields.Char()
    kv_number = fields.Char()
    date_document = fields.Char()
    posting_date = fields.Char()
    supplier_invoice_number = fields.Char()
    inv_amount = fields.Char()
    deposit = fields.Boolean()
    advance_deposit = fields.Char()
    fin_lease = fields.Boolean()
    
    
    
    