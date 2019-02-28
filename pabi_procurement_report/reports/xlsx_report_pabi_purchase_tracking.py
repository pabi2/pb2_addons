# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api


class XLSXReportPabiPurchaseTracking(models.TransientModel):
    _name = 'xlsx.report.pabi.purchase.tracking'
    _inherit = 'xlsx.report'

    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
    )
    pr_ids = fields.Many2many(
        'purchase.request',
        string='PR doc',
    )
    pr_date_from = fields.Date(
        string='PR Date From',
    )
    pr_date_to = fields.Date(
        string='PR Date To',
    )
    pr_requester_ids = fields.Many2many(
        'res.partner',
        string='Requested by(PR)',
    )
    pr_responsible_ids = fields.Many2many(
        'res.partner',
        string='Responsible Person(PR)',
    )
    po_ids = fields.Many2many(
        'purchase.order',
        string='PO doc',
    )
    po_date_from = fields.Date(
        string='PO Date From',
    )
    po_date_to = fields.Date(
        string='PO Date To',
    )
    po_responsible_ids = fields.Many2many(
        'res.partner',
        string='Responsible Person(PO)',
    )
    org_name = fields.Char(
        string='Org',
    )
    budget_name = fields.Char(
        string='Budget',
    )
    pr_number = fields.Char(
        string='PR doc',
    )
    po_number = fields.Char(
        string='PO doc',
    )
    pr_requester_name = fields.Char(
        string='Requested by(PR)',
    )
    pr_responsible_name = fields.Char(
        string='Responsible Person(PR)',
    )
    po_responsible_name = fields.Char(
        string='Responsible Person(PO)',
    )
    pr_date = fields.Char(
        string='PO Date',
    )
    po_date = fields.Char(
        string='PO Date',
    )
    
    
    # Report Result
    results = fields.Many2many(
        'xlsx.report.pabi.purchase.tracking.results',
        string='Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

    @api.onchange('org_ids', 'chartfield_ids', 'pr_date_from', 'pr_date_to', 'pr_requester_ids', 'pr_responsible_ids')
    def onchange_pr_domain(self):
        dom = []
        if self.org_ids:
            res = []
            operating_unit_ids = []
            for org in self.org_ids:
                res += [org.operating_unit_id.id]
            operating_unit_ids = self.env['operating.unit'].search([('id', 'in', res)])
            dom += [('operating_unit_id', 'in', operating_unit_ids.ids)]
        if self.chartfield_ids:
            res = []
            costcenter_ids = []
            for bud in self.chartfield_ids:
                res += [bud.costcenter_id.id]
            costcenter_ids = self.env['res.costcenter'].search([('id', 'in', res)])
            dom += [('line_ids.costcenter_id', 'in', costcenter_ids.ids)]
        if self.pr_date_from:
            dom += [('date_approve', '>=', self.pr_date_from)]
        if self.pr_date_to:
            dom += [('date_approve', '<=', self.pr_date_to)]
        if self.pr_requester_ids:
            dom += [('requested_by', 'in', self.pr_requester_ids.ids)]
        if self.pr_responsible_ids:
            dom += [('responsible_uid', 'in', self.pr_responsible_ids.ids)]
        return {'domain': {'pr_ids': (dom)}}
    
    
    @api.onchange('org_ids', 'chartfield_ids', 'po_date_from', 'po_date_to', 'po_responsible_ids')
    def onchange_po_domain(self):
        dom = []
        if self.org_ids:
            res = []
            operating_unit_ids = []
            for org in self.org_ids:
                res += [org.operating_unit_id.id]
            operating_unit_ids = self.env['operating.unit'].search([('id', 'in', res)])
            dom += [('operating_unit_id', 'in', operating_unit_ids.ids)]
        if self.chartfield_ids:
            res = []
            costcenter_ids = []
            for bud in self.chartfield_ids:
                res += [bud.costcenter_id.id]
            costcenter_ids = self.env['res.costcenter'].search([('id', 'in', res)])
            dom += [('order_line.costcenter_id', 'in', costcenter_ids.ids)]
        if self.po_date_from:
            dom += [('date_reference', '>=', self.po_date_from)]
        if self.po_date_to:
            dom += [('date_reference', '<=', self.po_date_to)]
        if self.po_responsible_ids:
            dom += [('responsible_uid', 'in', self.po_responsible_ids.ids)]
        return {'domain': {'po_ids': (dom)}}
      
    @api.onchange('org_ids', 'chartfield_ids')
    def onchange_org_id(self):
        res_org, res_bud = '', ''
        for org in self.org_ids:
            if res_org != '':
                res_org += ', '
            res_org += str(org.name_short)
        self.org_name = res_org

        for prg in self.chartfield_ids:
            if res_bud != '':
                res_bud += ', '
            res_bud += '['+str(prg.costcenter_id.code)+'] '+str(prg.costcenter_id.name_short)
        self.budget_name = res_bud
        
    @api.onchange('pr_ids','pr_requester_ids', 'pr_responsible_ids', 'pr_date_from', 'pr_date_to')  
    def onchange_pr_ids(self):
        res_pr, res_req, res_resp, res_date = '', '', '', ''
        for pr in self.pr_ids:
            if res_pr != '':
                res_pr += ', '
            res_pr += str(pr.name)
        self.pr_number = res_pr
        
        for pr_req in self.pr_requester_ids:
            if res_req != '': 
                res_req += ', '
            res_req += pr_req.name
        self.pr_requester_name = res_req
      
        for pr_resp in self.pr_responsible_ids:
            if res_resp != '': 
                res_resp += ', '
            res_resp += pr_resp.name
        self.pr_responsible_name = res_resp
        
        if self.pr_date_from and self.pr_date_to:
            res_date = str(self.pr_date_from)+' - '+str(self.pr_date_to)
        elif self.pr_date_from:
            res_date =str(self.pr_date_from)
        elif self.pr_date_to:
            res_date = str(self.pr_date_to)
        self.pr_date = res_date
         
    @api.onchange('po_ids', 'po_responsible_ids', 'po_date_from', 'po_date_to')  
    def onchange_po_ids(self):
        res_po, res_resp, res_date = '', '', ''
        for po in self.po_ids:
            if res_po != '':
                res_po += ', '
            res_po += str(po.name)
        self.po_number = res_po

        for po_resp in self.po_responsible_ids:
            if res_resp != '':
                res_resp += ', '
            res_resp += po_resp.name
        self.po_responsible_name = res_resp
    
        if self.po_date_from and self.po_date_to:
            res_date = str(self.po_date_from)+' - '+str(self.po_date_to)
        elif self.po_date_from:
            res_date =str(self.po_date_from)
        elif self.po_date_to:
            res_date = str(self.po_date_to)
        self.po_date = res_date


    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['xlsx.report.pabi.purchase.tracking.results']
        dom = []
        if self.org_ids:
            dom += [('org_id', 'in', self.org_ids.ids)]
        if self.chartfield_ids:
            res = []
            for cct in self.chartfield_ids:
                res += [cct.costcenter_id.id]
            dom += [('costcenter_id', 'in', res)]
        if self.pr_ids:
            dom += [('pr_id', 'in', self.pr_ids.ids)]
        if self.pr_date_from:
            dom += [('pr_date', '>=', self.pr_date_from)]
        if self.pr_date_to:
            dom += [('pr_date', '<=', self.pr_date_to)]
        if self.pr_requester_ids:
            dom += [('pr_requester_id', 'in', self.pr_requester_ids.ids)]
        if self.pr_responsible_ids:
            dom += [('pr_responsible_id', 'in', self.pr_responsible_ids.ids)]
        if self.po_ids:
            dom += [('po_id', 'in', self.pr_ids._ids)]
        if self.po_date_from:
            dom += [('po_date', '>=', self.po_date_from)]
        if self.po_date_to:
            dom += [('po_date', '<=', self.po_date_to)]
        if self.po_responsible_ids:
            dom += [('po_responsible_id', 'in', self.po_responsible_ids.ids)]
        print '-------------------------dom--', dom
        self.results = Result.search(dom)



class XLSXReportPabiPurchaseRequestTracking(models.Model):
    _name = 'xlsx.report.pabi.purchase.tracking.results'
    _auto = False
    _description = 'Temp table as ORM holder'


    org_id = fields.Many2one(
        'res.org',
        string='Org',
    )
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
    )
    pr_id = fields.Many2one(
        'purchase.request',
        string='PR doc',
    )
    pr_date = fields.Date(
        string='PR Date',
    )
    pr_requester_id = fields.Many2one(
        'res.partner',
        string='Requested by(PR)',
    )
    pr_responsible_id = fields.Many2one(
        'res.partner',
        string='Responsible Person(PR)',
    )
    po_id = fields.Many2one(
        'purchase.order',
        string='PO doc',
    )
    po_date = fields.Date(
        string='PO Date',
    )
    po_responsible_id = fields.Many2one(
        'res.partner',
        string='Responsible Person(PO)',
    )
    

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT 
        org.id as "org_id", cct.id as "costcenter_id", pr.id as "pr_id", pr.date_start as "pr_date", pr.name as "pr_name", 
        (SELECT part.id FROM res_users uer left join res_partner part on part.id = uer.partner_id
        WHERE uer.id = pr.requested_by) as "pr_requester_id",
        (SELECT part.display_name2 FROM res_users uer left join res_partner part on part.id = uer.partner_id
        WHERE uer.id = pr.requested_by) as "pr_requested", pr.date_approve as "pr_date_approve", 
        (SELECT part.id FROM res_users uer left join res_partner part on part.id = uer.partner_id
        WHERE uer.id = pr.responsible_uid) as "pr_responsible_id",
        (SELECT part.display_name2 FROM res_users uer left join res_partner part on part.id = uer.partner_id
        WHERE uer.id = pr.responsible_uid) as "pr_responsible", pr.objective as "pr_objective", pr.amount_total as "pr_amount_total", 
        (CASE
            WHEN prl.section_id is not null THEN (
                select concat('[',cos.code, ']', cos.name_short)
                from purchase_request_line
                left join res_section sect on sect.id = prl.section_id 
                left join res_costcenter cos on cos.id = sect.costcenter_id
                LIMIT 1)
            WHEN prl.project_id is not null THEN (
                select concat('[',cos.code, ']', cos.name)
                from purchase_request_line
                left join res_project pro on pro.id = prl.project_id
                left join res_costcenter cos on cos.id = pro.costcenter_id                                
                LIMIT 1)                    
            WHEN prl.invest_asset_id is not null THEN (
                select concat('[',cos.code, ']', cos.name)
                from purchase_request_line  
                left join res_invest_asset asset on asset.id = prl.invest_asset_id
                left join res_costcenter cos on cos.id = asset.costcenter_id
                LIMIT 1)
            WHEN prl.invest_construction_phase_id is not null THEN (
                select concat('[',cos.code, ']', cos.name)
                from purchase_request_line  
                left join res_invest_construction_phase icp on icp.id = prl.invest_construction_phase_id
                left join res_costcenter cos on cos.id = icp.costcenter_id
                LIMIT 1)
            WHEN prl.personnel_costcenter_id is not null THEN (
                select concat('[',cos.code, ']', cos.name) 
                from purchase_request_line
                left join res_personnel_costcenter rpc on rpc.id = prl.personnel_costcenter_id
                left join res_costcenter cos on cos.id = rpc.costcenter_id
                LIMIT 1)
        END) as "pr_budget", pd.name as "pd_name", pd.ordering_date as "pd_ordering_date", pd.date_doc_approve as "pd_date_doc_approve",
        po.id as "po_id", po.name as "po_name", po.date_order as "po_date", po.date_contract_start as "po_date_contract_start", 
        po.date_contract_end as "po_date_contract_end", poc.display_code as "po_display_code", poc.start_date as "po_start_date", 
        poc.end_date as "po_end_date",
        (SELECT part.id FROM res_users uer left join res_partner part on part.id = uer.partner_id
        WHERE uer.id = po.responsible_uid) as "po_responsible_id",
        (SELECT part.display_name2 FROM res_partner part WHERE part.id = po.partner_id) as "po_partner", pol.docline_seq as "pol_docline_seq", 
        (SELECT prod.name_template FROM product_product prod WHERE prod.id = pol.product_id) as "pol_product", pol.name as "pol_name",
        pol.date_planned as "pol_date_planned", 
        (CASE
            WHEN pol.section_id is not null THEN (
                select concat('[',cos.code, ']', cos.name_short)
                from purchase_order_line
                left join res_section sect on sect.id = pol.section_id 
                left join res_costcenter cos on cos.id = sect.costcenter_id
                LIMIT 1)
            WHEN pol.project_id is not null THEN (
                select concat('[',cos.code, ']', cos.name)
                from purchase_order_line
                left join res_project pro on pro.id = pol.project_id
                left join res_costcenter cos on cos.id = pro.costcenter_id                                
                LIMIT 1)                    
            WHEN pol.invest_asset_id is not null THEN (
                select concat('[',cos.code, ']', cos.name)
                from purchase_order_line  
                left join res_invest_asset asset on asset.id = pol.invest_asset_id
                left join res_costcenter cos on cos.id = asset.costcenter_id
                LIMIT 1)
            WHEN pol.invest_construction_phase_id is not null THEN (
                select concat('[',cos.code, ']', cos.name)
                from purchase_order_line  
                left join res_invest_construction_phase icp on icp.id = pol.invest_construction_phase_id
                left join res_costcenter cos on cos.id = icp.costcenter_id
                LIMIT 1)
            WHEN pol.personnel_costcenter_id is not null THEN (
                select concat('[',cos.code, ']', cos.name) 
                from purchase_order_line
                left join res_personnel_costcenter rpc on rpc.id = pol.personnel_costcenter_id
                left join res_costcenter cos on cos.id = rpc.costcenter_id
                LIMIT 1)
        END) as "po_budget", (SELECT fund.name FROM res_fund fund WHERE fund.id = pol.fund_id) as "pol_fund", 
        (SELECT cct.name FROM cost_control cct WHERE cct.id = pol.cost_control_id) as "pol_cost_control", pol.product_qty as "pol_product_qty", 
        (SELECT uom.name FROM product_uom uom WHERE uom.id = pol.product_uom) as "pol_product_uom", 
        pol.price_unit as "pol_price_unit", pol.price_unit*pol.product_qty as "pol_sub_total", 
        (SELECT cur.name FROM res_currency cur WHERE cur.id = po.currency_id) as "pol_currency", 
        (SELECT fyear.name FROM account_fiscalyear fyear WHERE fyear.id = pol.fiscalyear_id) as "pol_fiscalyear", 
        (SELECT part.display_name2 FROM res_partner part WHERE part.id = po.responsible_uid) as "po_responsible",
        (SELECT payterm.name FROM account_payment_term payterm WHERE payterm.id = po.payment_term_id) as "po_payment_term", 
        pwa.name as "pwa_name", sp.name as "sp_name", pwa.date_accept as "pwq_date_accept", pb.name as "pb_name", 
        pb.date_sent as "pb_date_sent", pb.date as "pb_date", inv.number as "inv_name", inv.date_invoice as "inv_date_invoice", 
        (SELECT part.display_name2 FROM res_users uer left join res_partner part on part.id = uer.partner_id 
         WHERE uer.id = inv.user_id) as "inv_user", vou.number as "vou_name", vou.date as "vou_date", vou.date_value as "vou_date_value"
        
        FROM purchase_request pr
        LEFT join purchase_request_line prl
        ON prl.request_id = pr.id 
        LEFT JOIN purchase_request_purchase_requisition_line_rel prpdrel
        ON prpdrel.purchase_request_line_id = prl.id
        LEFT JOIN purchase_requisition_line pdl
        ON prpdrel.purchase_requisition_line_id = pdl.id
        LEFT JOIN purchase_requisition pd
        ON pd.id = pdl.requisition_id
        LEFT JOIN purchase_contract poc
        ON poc.requisition_id = pd.id
        LEFT JOIN purchase_order po
        ON po.requisition_id = pd.id
        LEFT JOIN purchase_order_line pol
        ON pol.requisition_line_id = pdl.id
        LEFT JOIN purchase_work_acceptance pwa
        ON pwa.order_id = po.id
        LEFT JOIN stock_picking sp
        ON sp.acceptance_id = pwa.id
        LEFT JOIN account_invoice inv
        ON inv.source_document = po.name
        LEFT JOIN account_invoice_line invl
        ON invl.invoice_id = inv.id
        LEFT JOIN purchase_billing pb
        ON pb.id = inv.purchase_billing_id
        left join account_voucher_line voul 
        on voul.invoice_id = inv.id 
        LEFT JOIN account_voucher vou
        ON vou.id = voul.voucher_id
        LEFT JOIN operating_unit org
        ON org.id = pr.operating_unit_id and org.id = po.operating_unit_id
        LEFT JOIN res_costcenter cct
        ON cct.id = prl.costcenter_id and cct.id = pol.costcenter_id
        order by pr.id, po.id, inv.name, vou.name)""" % (self._table, ))