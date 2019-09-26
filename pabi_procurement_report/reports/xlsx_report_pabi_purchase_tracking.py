# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api
from openerp.exceptions import except_orm, ValidationError

class XLSXReportPabiPurchaseTracking(models.TransientModel):
    _name = 'xlsx.report.pabi.purchase.tracking'
    _inherit = 'xlsx.report'

    org_ids = fields.Many2many('res.org', string='Org',)
    chartfield_ids = fields.Many2many('chartfield.view', string='Budget',)
    pr_ids = fields.Many2many('purchase.request', string='PR doc',)
    pr_date_from = fields.Date(string='PR Date From',)
    pr_date_to = fields.Date(string='PR Date To',)
    pr_requester_ids = fields.Many2many('res.partner', string='Requested by(PR)',)
    pr_responsible_ids = fields.Many2many('res.partner', string='Responsible Person(PR)',)
    po_ids = fields.Many2many('purchase.order', string='PO doc', domain="[('name','not like', 'RFQ%')]",)
    po_date_from = fields.Date(string='PO Date From',)
    po_date_to = fields.Date(string='PO Date To',)
    po_responsible_ids = fields.Many2many('res.partner', string='Responsible Person(PO)',)
    org_name = fields.Char(string='Org',)
    budget_name = fields.Char(string='Budget',)
    pr_number = fields.Char(string='PR doc',)
    po_number = fields.Char(string='PO doc',)
    pr_requester_name = fields.Char(string='Requested by(PR)',)
    pr_responsible_name = fields.Char(string='Responsible Person(PR)',)
    po_responsible_name = fields.Char(string='Responsible Person(PO)',)
    pr_date = fields.Char(string='PO Date',)
    po_date = fields.Char(string='PO Date',)
    data_view = fields.Selection([('pr', 'Purchase Requests'),('po', 'Purchase Order'),], string='Data From', default='pr', required=True)
    
    # Report Result
    pr_results = fields.Many2many(
        'xlsx.report.pabi.purchase.tracking.results',
        string='PR Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )
    po_results = fields.Many2many(
        'xlsx.report.pabi.purchase.tracking.results.order',
        string='PO Results',
        compute='_compute_results',
        help="Use compute fields, so there is nothing store in database",
    )

      
    @api.onchange('org_ids', 'chartfield_ids')
    def onchange_org_id(self):
        res_org, res_bud = '', ''
        for org in self.org_ids:
            name = self.env['operating.unit'].search([('id', '=', org.operating_unit_id.id)]).name
            if res_org != '': 
                res_org += ', '+name
            else: res_org += name
        ##org_name
        self.org_name = res_org

        for prg in self.chartfield_ids:
            if res_bud != '':
                res_bud += ', '
            res_bud += '['+str(prg.code)+'] '+str(prg.name_short or prg.name)
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
       
    @api.onchange('data_view')  
    def onchange_data_view(self):
    
        if self.data_view == 'po':
            self.pr_ids = False
            self.pr_requester_ids = False
            self.pr_responsible_ids = False
            self.pr_date_from = False
            self.pr_date_to = False
            self.pr_number = False
            self.pr_requester_name = False
            self.pr_responsible_name = False
            self.pr_date = False
        elif self.data_view == 'pr':
            self.po_ids = False
            self.po_responsible_ids = False
            self.po_date_from = False
            self.po_date_to = False
            self.po_number = False
            self.po_responsible_name = False
            self.po_date = False


    @api.multi
    def _compute_results(self):
        self.ensure_one()
        PR_Result = self.env['xlsx.report.pabi.purchase.tracking.results']
        PO_Result = self.env['xlsx.report.pabi.purchase.tracking.results.order']
        dom = []
        if self.org_ids:
            res = []
            operating_unit_ids = []
            for org in self.org_ids:
                res += [org.operating_unit_id.id]
            operating_unit_ids = self.env['operating.unit'].search([('id', 'in', res)])
            dom += [('org_id', 'in', operating_unit_ids.ids)]
        if self.chartfield_ids:
            dom += ['|', ('prl_budget', 'in', self.chartfield_ids.ids), ('pol_budget', 'in', self.chartfield_ids.ids)]
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
            dom += [('po_id', 'in', self.po_ids.ids)]
        if self.po_date_from:
            dom += [('po_date', '>=', self.po_date_from)]
        if self.po_date_to:
            dom += [('po_date', '<=', self.po_date_to)]
        if self.po_responsible_ids:
            dom += [('po_responsible_id', 'in', self.po_responsible_ids.ids)]
        
        # Export Excel
        if self.data_view == 'pr': 
            pr_results_0 = PR_Result.search(dom)
            self.pr_results = pr_results_0
        elif self.data_view == 'po': 
            po_results_0 = PO_Result.search(dom)
            self.po_results = po_results_0
            
        return True


class XLSXReportPabiPurchaseRequestTracking(models.Model):
    _name = 'xlsx.report.pabi.purchase.tracking.results'
    _auto = False
    _description = 'Temp table as ORM holder'

    org_id = fields.Many2one('operating.unit', string='Org',)
    #costcenter_id = fields.Many2one('res.costcenter', string='Costcenter',)
    pr_id = fields.Many2one( 'purchase.request', string='PR doc',)
    pr_date = fields.Date( string='PR Date',)
    pr_requester_id = fields.Many2one('res.partner', string='Requested by(PR)',)
    pr_responsible_id = fields.Many2one('res.partner', string='Responsible Person(PR)',)
    prl_id = fields.Many2one('purchase.request.line', string='PR line',)
    prl_budget = fields.Many2one('chartfield.view', string='PR line Budget',)
    pd_id = fields.Many2one('purchase.requisition', string='PD id',)
    po_id = fields.Many2one('purchase.order', string='PO doc',)
    po_name = fields.Char(string='PO number',)
    po_date = fields.Date(string='PO Date',)
    po_responsible_id = fields.Many2one('res.partner', string='Responsible Person(PO)',)
    pol_id = fields.Many2one('purchase.order.line', string='PO line',)
    pol_budget = fields.Many2one('chartfield.view', string='PO line Budget',)
    pol_state = fields.Char(string='PO line State',)
    poc_id = fields.Many2one('purchase.contract', string='POC id',)
    pwa_id = fields.Many2one('purchase.work.acceptance', string='PWA id',)
    sp_id = fields.Many2one('stock.picking', string='SP id',)
    inv_id = fields.Many2one('account.invoice', string='Invoice id',)
    pb_id = fields.Many2one('purchase.billing', string='PB id',)
    vou_id = fields.Many2one('account.voucher', string='Voucher id',)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT row_number() over (order by pr.id) as id,
            ou.id as org_id, pr.id as pr_id, pr.date_start as pr_date, 
            users.partner_id as pr_requester_id, pr_res.partner_id as pr_responsible_id, prl.id as prl_id,
            (CASE
                WHEN prl.section_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_section sect on sect.id = prl.section_id 
                    left join chartfield_view chv on chv.code = sect.code
                    LIMIT 1)
                WHEN prl.invest_construction_phase_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_invest_construction_phase icp on icp.id = prl.invest_construction_phase_id
                    left join chartfield_view chv on chv.code = icp.code
                    LIMIT 1)
                WHEN prl.project_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_project pro on pro.id = prl.project_id
                    left join chartfield_view chv on chv.code = pro.code                            
                    LIMIT 1)                    
                WHEN prl.invest_asset_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_invest_asset iat on iat.id = prl.invest_asset_id
                    left join chartfield_view chv on chv.code = iat.code
                    LIMIT 1)
                WHEN prl.personnel_costcenter_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_personnel_costcenter rpc on rpc.id = prl.personnel_costcenter_id
                    left join chartfield_view chv on chv.code = rpc.code
                    LIMIT 1)
            END) as prl_budget,
            pd.id as pd_id, po.id as po_id, po.name as po_name, po.date_order as po_date, 
            po_res.partner_id as po_responsible_id, pol.id as pol_id,
            (CASE
                WHEN pol.section_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_section sect on sect.id = pol.section_id 
                    left join chartfield_view chv on chv.code = sect.code
                    LIMIT 1)
                WHEN pol.invest_construction_phase_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_invest_construction_phase icp on icp.id = pol.invest_construction_phase_id
                    left join chartfield_view chv on chv.code = icp.code
                    LIMIT 1)
                WHEN pol.project_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_project pro on pro.id = pol.project_id
                    left join chartfield_view chv on chv.code = pro.code                            
                    LIMIT 1)                    
                WHEN pol.invest_asset_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_invest_asset iat on iat.id = pol.invest_asset_id
                    left join chartfield_view chv on chv.code = iat.code
                    LIMIT 1)
                WHEN pol.personnel_costcenter_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_personnel_costcenter rpc on rpc.id = pol.personnel_costcenter_id
                    left join chartfield_view chv on chv.code = rpc.code
                    LIMIT 1)
            END) as pol_budget,
            pol.state as pol_state, poc.id as poc_id, pwa.id as pwa_id, sp.id as sp_id, inv.id as inv_id, pb.id as pb_id, vou.id as vou_id
        FROM purchase_request pr
        LEFT join purchase_request_line prl ON prl.request_id = pr.id 
        LEFT JOIN purchase_request_purchase_requisition_line_rel prpdrel ON prpdrel.purchase_request_line_id = prl.id
        LEFT JOIN purchase_requisition_line pdl ON prpdrel.purchase_requisition_line_id = pdl.id
        LEFT JOIN purchase_requisition pd ON pd.id = pdl.requisition_id
        LEFT JOIN purchase_contract poc ON poc.requisition_id = pd.id
        LEFT JOIN purchase_order po ON po.requisition_id = pd.id
        LEFT JOIN purchase_order_line pol ON pol.requisition_line_id = pdl.id
        LEFT JOIN purchase_work_acceptance pwa ON pwa.order_id = po.id
        LEFT JOIN res_users pr_res ON pr_res.id = pr.responsible_uid
        LEFT JOIN res_users po_res ON po_res.id = po.responsible_uid
        LEFT JOIN res_users users ON users.id = pr.requested_by
        LEFT JOIN stock_picking sp ON sp.acceptance_id = pwa.id
        LEFT JOIN account_invoice inv ON inv.source_document = po.name
        LEFT JOIN purchase_billing pb ON pb.id = inv.purchase_billing_id 
        LEFT JOIN account_voucher_line voul ON voul.invoice_id = inv.id 
        LEFT JOIN account_voucher vou ON vou.id = voul.voucher_id
        LEFT JOIN operating_unit ou ON ou.id = pr.operating_unit_id or ou.id = po.operating_unit_id
        where (pol.state != 'cancel' and po.name not like 'RFQ%%') or po.id is null
        order by pr.id, po.id, inv.name, vou.name
        )""" % (self._table, ))




class XLSXReportPabiPurchaseRequestTrackingOrder(models.Model):
    _name = 'xlsx.report.pabi.purchase.tracking.results.order'
    _auto = False
    _description = 'Temp table as ORM holder'

    org_id = fields.Many2one('operating.unit', string='Org',)
    #costcenter_id = fields.Many2one('res.costcenter', string='Costcenter',)
    pr_id = fields.Many2one( 'purchase.request', string='PR doc',)
    pr_date = fields.Date( string='PR Date',)
    pr_requester_id = fields.Many2one('res.partner', string='Requested by(PR)',)
    pr_responsible_id = fields.Many2one('res.partner', string='Responsible Person(PR)',)
    prl_id = fields.Many2one('purchase.request.line', string='PR line',)
    prl_budget = fields.Many2one('chartfield.view', string='PR line Budget',)
    pd_id = fields.Many2one('purchase.requisition', string='PD id',)
    po_id = fields.Many2one('purchase.order', string='PO doc',)
    po_name = fields.Char(string='PO number',)
    po_date = fields.Date(string='PO Date',)
    po_responsible_id = fields.Many2one('res.partner', string='Responsible Person(PO)',)
    pol_id = fields.Many2one('purchase.order.line', string='PO line',)
    pol_budget = fields.Many2one('chartfield.view', string='PO line Budget',)
    pol_state = fields.Char(string='PO line State',)
    poc_id = fields.Many2one('purchase.contract', string='POC id',)
    pwa_id = fields.Many2one('purchase.work.acceptance', string='PWA id',)
    sp_id = fields.Many2one('stock.picking', string='SP id',)
    inv_id = fields.Many2one('account.invoice', string='Invoice id',)
    pb_id = fields.Many2one('purchase.billing', string='PB id',)
    vou_id = fields.Many2one('account.voucher', string='Voucher id',)

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
        SELECT row_number() over (order by pr.id) as id,
            ou.id as org_id, pr.id as pr_id, pr.date_start as pr_date, 
            users.partner_id as pr_requester_id, pr_res.partner_id as pr_responsible_id, prl.id as prl_id,
            (CASE
                WHEN prl.section_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_section sect on sect.id = prl.section_id 
                    left join chartfield_view chv on chv.code = sect.code
                    LIMIT 1)
                WHEN prl.invest_construction_phase_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_invest_construction_phase icp on icp.id = prl.invest_construction_phase_id
                    left join chartfield_view chv on chv.code = icp.code
                    LIMIT 1)
                WHEN prl.project_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_project pro on pro.id = prl.project_id
                    left join chartfield_view chv on chv.code = pro.code                            
                    LIMIT 1)                    
                WHEN prl.invest_asset_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_invest_asset iat on iat.id = prl.invest_asset_id
                    left join chartfield_view chv on chv.code = iat.code
                    LIMIT 1)
                WHEN prl.personnel_costcenter_id is not null THEN (
                    select chv.id
                    from purchase_request_line
                    left join res_personnel_costcenter rpc on rpc.id = prl.personnel_costcenter_id
                    left join chartfield_view chv on chv.code = rpc.code
                    LIMIT 1)
            END) as prl_budget,
            pd.id as pd_id, po.id as po_id, po.name as po_name, po.date_order as po_date, 
            po_res.partner_id as po_responsible_id, pol.id as pol_id,
            (CASE
                WHEN pol.section_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_section sect on sect.id = pol.section_id 
                    left join chartfield_view chv on chv.code = sect.code
                    LIMIT 1)
                WHEN pol.invest_construction_phase_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_invest_construction_phase icp on icp.id = pol.invest_construction_phase_id
                    left join chartfield_view chv on chv.code = icp.code
                    LIMIT 1)
                WHEN pol.project_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_project pro on pro.id = pol.project_id
                    left join chartfield_view chv on chv.code = pro.code                            
                    LIMIT 1)                    
                WHEN pol.invest_asset_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_invest_asset iat on iat.id = pol.invest_asset_id
                    left join chartfield_view chv on chv.code = iat.code
                    LIMIT 1)
                WHEN pol.personnel_costcenter_id is not null THEN (
                    select chv.id
                    from purchase_order_line
                    left join res_personnel_costcenter rpc on rpc.id = pol.personnel_costcenter_id
                    left join chartfield_view chv on chv.code = rpc.code
                    LIMIT 1)
            END) as pol_budget,
            pol.state as pol_state, poc.id as poc_id, pwa.id as pwa_id, sp.id as sp_id, inv.id as inv_id, pb.id as pb_id, vou.id as vou_id
        FROM purchase_order po
        LEFT JOIN purchase_requisition pd ON pd.id = po.requisition_id
        LEFT JOIN purchase_contract poc ON poc.requisition_id = pd.id
        LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
        LEFT JOIN purchase_requisition_line pdl ON pdl.id = pol.requisition_line_id
        LEFT JOIN purchase_request_purchase_requisition_line_rel prpdrel ON prpdrel.purchase_requisition_line_id = pdl.id
        LEFT join purchase_request_line prl ON prl.id = prpdrel.purchase_request_line_id
        LEFT join purchase_request pr ON pr.id = prl.request_id
        LEFT JOIN purchase_work_acceptance pwa ON pwa.order_id = po.id
        LEFT JOIN res_users pr_res ON pr_res.id = pr.responsible_uid
        LEFT JOIN res_users po_res ON po_res.id = po.responsible_uid
        LEFT JOIN res_users users ON users.id = pr.requested_by
        LEFT JOIN stock_picking sp ON sp.acceptance_id = pwa.id
        LEFT JOIN account_invoice inv ON inv.source_document = po.name
        LEFT JOIN purchase_billing pb ON pb.id = inv.purchase_billing_id 
        LEFT JOIN account_voucher_line voul ON voul.invoice_id = inv.id 
        LEFT JOIN account_voucher vou ON vou.id = voul.voucher_id
        LEFT JOIN operating_unit ou ON ou.id = pr.operating_unit_id or ou.id = po.operating_unit_id
        LEFT JOIN res_org org ON org.id = ou.org_id
        where (pol.state != 'cancel' and po.name not like 'RFQ%%')
        order by pr.id, po.id, inv.name, vou.name
        )""" % (self._table, ))

