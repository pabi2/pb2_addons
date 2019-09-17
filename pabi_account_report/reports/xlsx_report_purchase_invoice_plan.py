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
        'report.purchase.invoice.plan.view',
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
        plan_ids = []
        chartfield_dom = ''
        InvoicePlan = self.env['purchase.invoice.plan']
        Reports = self.env['report.purchase.invoice.plan.view']
        dom = [('po.use_invoice_plan','=',True)]
        
        if self.org_ids:
            dom += [('org.id', 'in', tuple(self.org_ids.ids))]
        if self.purchase_ids:
            dom += [('po.id', 'in', tuple(self.purchase_ids.ids))]
        if self.contract_ids:
            dom += [('pct.id', 'in', tuple(self.contract_ids.ids))]
        if self.account_ids:
            dom += [('rpt.account_id', 'in', tuple(self.account_ids.ids))]
        if self.chartfield_ids:
            
            chartfield_dom = self.get_where_str_chartfield()
        
        if self.date_po_start and not self.date_po_end:
            dom += [('cast(po.date_order as date)','=',self.date_po_start)]
        if self.date_po_start and self.date_po_end:
            dom += [('cast(po.date_order as date)','>=',self.date_po_start),('cast(po.date_order as date)','<=',self.date_po_end)]
        if self.date_start:
            dom += [('cast(po.date_order as date)','>=',self.date_start)]
        if self.date_end:
            dom += [('cast(po.date_order as date)','<=',self.date_end)]
        if self.period_start_id:
            dom += [('po.date_order as date)','>=',self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('cast(po.date_order as date)','<=',self.period_end_id.date_stop)]
        if self.date_contract_action_start:
            dom += [('pct.action_date','>=',self.date_contract_action_start)]
        if self.date_contract_action_end:
            dom += [('pct.action_date','<=',self.date_contract_action_end)]
        
        where_str = self._domain_to_where_str(dom)
        where_str += chartfield_dom
        
        self._cr.execute("""
            select * from (
                (select pol.org_id as org_id, po.id as purchase_id, pct.id as contract_id, pip.id as inv_plan_id, av.id as invoice_id, 
                    av.purchase_billing_id as billing_id, pol.id as purchase_line_id, po.account_deposit_supplier as account_id, 
                    prod.id as product_id, po.partner_id as supplier_id,
                    fis.name as po_fiscalyear, ou.name as org, po.date_order, po.name as po_number, pol.docline_seq, pip.installment,
                    case
                        when po.po_contract_type_id is not null then po_pct_t.name
                        when po.contract_id is not null then pct_t.name
                        else ''
                    end as po_contract_type,
                    ag.name as activity_group, 
                    rpt.name as activity_rpt,
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
                    fund.name as fund, fis.name as fiscal_year_by_invoice_plan,
                    cur_po.name as currency, 
                    (SELECT STRING_AGG(tax.description, ', ') AS tax 
                     FROM account_tax tax 
                         LEFT JOIN purchase_order_taxe pot ON pot.tax_id = tax.id
                     WHERE pot.ord_id = pol.id
                    ) AS taxes,
                    ROUND((CASE
                        WHEN cur_po.name = 'THB' THEN 1
                        WHEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_po.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1) IS NULL 
                        THEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_po.id and CAST(po.date_order AS DATE) > CAST(cur_r.name AS DATE) order by cur_r.name limit 1)
                        ELSE (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_po.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1)
                    END), 2) as exchange_rate_po,
                    ROUND((CASE
                        WHEN cur_kv.name = 'THB' THEN 1
                        WHEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_kv.id and av.date_invoice = CAST(cur_r.name AS DATE) limit 1) IS NULL 
                        THEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_kv.id and av.date_invoice  > CAST(cur_r.name AS DATE) order by cur_r.name limit 1)
                        ELSE (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_kv.id and av.date_invoice  = CAST(cur_r.name AS DATE) limit 1)
                    END), 2) as exchange_rate_kv,
                    (select wa.name from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as wa_number, 
                    (select wa.date_accept from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as acceptance_date,
                    (select wal.to_receive_qty from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as plan_qty,
                    (select wal.price_unit_untaxed from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as plan_unit_price,
                    (select wal.price_subtotal from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as subtotal,
                    (select invl.price_subtotal from account_invoice_line invl where invl.invoice_id = av.id and 
                        invl.purchase_line_id = pol.id
                    ) as inv_amount,
                    case
                        when po.use_deposit is False and po.use_advance is False then ''
                        else ads.name
                    end as advance_deposit
                from purchase_order po
                    left join purchase_order_line pol on pol.order_id = po.id
                    left join purchase_invoice_plan pip on pip.order_line_id = pol.id
                    left join account_fiscalyear fis on fis.id = pol.fiscalyear_id
                    left join purchase_contract pct on pct.id = po.contract_id
                    left join purchase_contract_type pct_t on pct_t.id = pct.contract_type_id
                    left join purchase_contract_type po_pct_t on po_pct_t.id = po.po_contract_type_id
                    left join account_activity_group ag on ag.id = pol.activity_group_id
                    left join account_activity rpt on rpt.id = pol.activity_rpt_id
                    left join product_product prod on prod.id = pol.product_id
                    left join res_org org on org.id = pol.org_id
                    left join operating_unit ou on ou.id = org.operating_unit_id
                    left join res_fund fund on fund.id = pol.fund_id
                    left join res_section sec on sec.id = pol.section_id
                    left join res_project prj on prj.id = pol.project_id
                    left join res_invest_asset asset on asset.id = pol.invest_asset_id
                    left join res_invest_construction_phase phase on phase.id = pol.invest_construction_phase_id
                    left join res_personnel_costcenter rpc on rpc.id = pol.personnel_costcenter_id
                    left join account_invoice av on av.id = pip.ref_invoice_id
                    left join res_currency cur_po on cur_po.id = po.currency_id
                    left join res_currency cur_kv on cur_kv.id = av.currency_id
                    left join account_account ads on ads.id = po.account_deposit_supplier
                where po.state not in ('except_picking','except_invoice','cancel') and po.order_type = 'purchase_order' and po.use_invoice_plan = True
                    and pip.order_line_id is null and pol.active = True and %s
                )
            union
                (select pol.org_id as org_id, po.id as purchase_id, pct.id as contract_id, pip.id as inv_plan_id, av.id as invoice_id, 
                    av.purchase_billing_id as billing_id, pol.id as purchase_line_id, po.account_deposit_supplier as account_id, 
                    prod.id as product_id, po.partner_id as supplier_id,
                    fis.name as po_fiscalyear, ou.name as org, po.date_order, po.name as po_number, pol.docline_seq, pip.installment,
                    case
                        when po.po_contract_type_id is not null then po_pct_t.name
                        when po.contract_id is not null then pct_t.name
                        else ''
                    end as po_contract_type,
                    ag.name as activity_group, 
                    rpt.name as activity_rpt,
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
                    fund.name as fund, fis.name as fiscal_year_by_invoice_plan,
                    cur_po.name as currency, 
                    (SELECT STRING_AGG(tax.description, ', ') AS tax 
                     FROM account_tax tax 
                         LEFT JOIN purchase_order_taxe pot ON pot.tax_id = tax.id
                     WHERE pot.ord_id = pol.id
                    ) AS taxes,
                    ROUND((CASE
                        WHEN cur_po.name = 'THB' THEN 1
                        WHEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_po.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1) IS NULL 
                        THEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_po.id and CAST(po.date_order AS DATE) > CAST(cur_r.name AS DATE) order by cur_r.name limit 1)
                        ELSE (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_po.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1)
                    END), 2) as exchange_rate_po,
                    ROUND((CASE
                        WHEN cur_kv.name = 'THB' THEN 1
                        WHEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_kv.id and av.date_invoice = CAST(cur_r.name AS DATE) limit 1) IS NULL 
                        THEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_kv.id and av.date_invoice  > CAST(cur_r.name AS DATE) order by cur_r.name limit 1)
                        ELSE (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                            WHERE cur_r.currency_id = cur_kv.id and av.date_invoice  = CAST(cur_r.name AS DATE) limit 1)
                    END), 2) as exchange_rate_kv,
                    (select wa.name from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as wa_number, 
                    (select wa.date_accept from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as acceptance_date,
                    (select wal.to_receive_qty from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as plan_qty,
                    (select wal.price_unit_untaxed from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as plan_unit_price,
                    (select wal.price_subtotal from purchase_work_acceptance_line wal 
                        left join purchase_work_acceptance wa on wa.id = wal.acceptance_id
                     where wal.line_id = pol.id and wa.state != 'cancel' and wa.installment = pip.installment limit 1
                    ) as subtotal,
                    (select invl.price_subtotal from account_invoice_line invl where invl.invoice_id = av.id and 
                        invl.purchase_line_id = pol.id
                    ) as inv_amount,
                    case
                        when po.use_deposit is False and po.use_advance is False then ''
                        else ads.name
                    end as advance_deposit
                from purchase_invoice_plan pip
                    left join purchase_order_line pol on pol.id = pip.order_line_id
                    left join purchase_order po on po.id = pip.order_id
                    left join account_fiscalyear fis on fis.id = pol.fiscalyear_id
                    left join purchase_contract pct on pct.id = po.contract_id
                    left join purchase_contract_type pct_t on pct_t.id = pct.contract_type_id
                    left join purchase_contract_type po_pct_t on po_pct_t.id = po.po_contract_type_id
                    left join account_activity_group ag on ag.id = pol.activity_group_id
                    left join account_activity rpt on rpt.id = pol.activity_rpt_id
                    left join product_product prod on prod.id = pol.product_id
                    left join res_org org on org.id = pol.org_id
                    left join operating_unit ou on ou.id = org.operating_unit_id
                    left join res_fund fund on fund.id = pol.fund_id
                    left join res_section sec on sec.id = pol.section_id
                    left join res_project prj on prj.id = pol.project_id
                    left join res_invest_asset asset on asset.id = pol.invest_asset_id
                    left join res_invest_construction_phase phase on phase.id = pol.invest_construction_phase_id
                    left join res_personnel_costcenter rpc on rpc.id = pol.personnel_costcenter_id
                    left join account_invoice av on av.id = pip.ref_invoice_id
                    left join res_currency cur_po on cur_po.id = po.currency_id
                    left join res_currency cur_kv on cur_kv.id = av.currency_id
                    left join account_account ads on ads.id = po.account_deposit_supplier
                where po.state not in ('except_picking','except_invoice','cancel') and po.order_type = 'purchase_order' and po.use_invoice_plan = True
                    and pol.active = True and %s)
            ) as new
            order by org_id, po_fiscalyear, date_order, po_number, docline_seq, installment
        """  % (where_str,where_str))
        
        invoice_plans = self._cr.dictfetchall()
        
        for line in invoice_plans:
            self.results += Reports.new(line)
        
        print 'results: '+str(self.results)
        
        
        
class ReportPurchaseInvoicePlanView(models.AbstractModel):
    _name = 'report.purchase.invoice.plan.view'
    #_auto = False
    
    org_id = fields.Many2one('res.org')
    purchase_id = fields.Many2one('purchase.order')
    contract_id = fields.Many2one('purchase.contract')
    account_id = fields.Many2one('account.account')
    inv_plan_id = fields.Many2one('purchase.invoice.plan')
    invoice_id = fields.Many2one('account.invoice')
    billing_id = fields.Many2one('purchase.billing')
    purchase_line_id = fields.Many2one('purchase.order.line')
    product_id = fields.Many2one('product.product')
    supplier_id = fields.Many2one('res.partner')
    po_fiscalyear = fields.Char()
    po_contract_type = fields.Char()
    activity_group = fields.Char()
    activity_rpt = fields.Char()
    budget_code = fields.Char()
    budget_name = fields.Char()
    fund = fields.Char()
    fiscal_year_by_invoice_plan = fields.Char()
    currency = fields.Char()
    taxes = fields.Char()
    exchange_rate_po = fields.Float()
    exchange_rate_kv = fields.Float()
    wa_number = fields.Char()
    acceptance_date = fields.Date()
    plan_qty = fields.Char()
    plan_unit_price = fields.Char()
    subtotal = fields.Char()
    inv_amount = fields.Float()
    advance_deposit = fields.Boolean()
