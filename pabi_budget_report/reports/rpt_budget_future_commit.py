# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from openerp.exceptions import ValidationError

class RPTBudgetFutureCommit(models.TransientModel):
    _name = 'rpt.budget.future.commit'
    _inherit = 'report.budget.common.multi'
    
    date_report = fields.Date(
        string='Report Date',
        #default=lambda self: fields.Date.context_today(self),
        #required=True,
    )
    results = fields.Many2many(
        'rpt.budget.future.commit.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    @api.multi
    def _compute_results(self):
        #dom = []
        self.ensure_one()
        date_report = self.date_report
        Result = self.env['rpt.budget.future.commit.line']
        
        dom = [('fiscalyear', '=', self.fiscalyear_id.name)]
        
        if self.report_type in ('unit_base','project_base','invest_asset','invest_construction'):
            dom += [('budget_view', '=', self.report_type)]
        
        
        self.results = Result.search([])
        
        print '\n results: '+str(self.results)
    
    
    @api.multi
    def run_jasper_report(self, data):
        self.ensure_one()
        
        data = {}
        data['parameters'] = {}
        #data['parameters']['ids'] = self.id
        ids = []
        for rec in self.results:
            ids.append(rec.id)
        data['parameters']['ids'] = ids
        data['parameters']['report_type'] = self.report_type
        data['parameters']['fiscal_year'] = self.fiscalyear_id.name
        #data['parameters']['budget_overview'] = self.
        #data['parameters']['org'] = self.
        #data['parameters']['budget'] = self.
        #data['parameters']['po_document'] = self.
        #data['parameters']['order_date'] = self.
        #data['parameters']['run_by'] = self.
        #data['parameters']['run_date'] = self.
        
        report_ids = 'pabi_budget_multi_report.rpt_budget_future_commit_report'
        data['report_ids'] = report_ids
        #return {
        #    'type': 'ir.actions.report.xml',
        #    'report_name': 'rpt_report_purchase_test',
        #    'datas': data,
        #}
        
        return super(RPTBudgetFutureCommit, self).run_jasper_report(data)
    
    
    @api.multi
    def _get_data_to_report(self):
        report_ids = 'pabi_budget_multi_report.rpt_budget_future_commit_report'
        commit_id = self.create({
                                    'xlsx_report': True,
                                    'async_process': True,
                                })
        commit_id.action_get_report()
        
    
    def _action_rpt_budget_future_commit(self, cr, uid, context=None):
        future_commit_obj = self.pool.get('rpt.budget.future.commit')
        
        future_commit_obj._get_data_to_report(cr, uid, [], context=context)
        
        
class RPTBudgetFutureCommitLine(models.Model):
    _name = 'rpt.budget.future.commit.line'
    _auto = False
    
    id = fields.Integer('ID')
    doc_number = fields.Char('doc_number')
    order_date = fields.Char('order_date')
    po_contract = fields.Char('po_contract')
    po_contract_type = fields.Char('po_contract_type')
    po_contract_start_date = fields.Char('po_contract_start_date')
    po_contract_end_date = fields.Char('po_contract_end_date')
    procurement_method = fields.Char('procurement_method')
    pr_reference_doc = fields.Char('pr_reference_doc')
    pd_reference_doc = fields.Char('pd_reference_doc')
    product = fields.Char('product')
    item = fields.Integer('item')
    description = fields.Char('description')
    scheduled_date = fields.Char('scheduled_date')
    product_cat = fields.Char('product_cat')
    gl = fields.Char('gl')
    gl_name = fields.Char('gl_name')
    activity_group_code = fields.Char('activity_group_code')
    activity_group_name = fields.Char('activity_group_name')
    activity_rpt_code = fields.Char('activity_rpt')
    activity_rpt_name = fields.Char('activity_rpt_name')
    budget_view = fields.Char('budget_view')
    budget_code = fields.Char('budget_code')
    budget_name = fields.Char('budget_name')
    fund = fields.Char('Fund')
    job_order = fields.Char('job_order')
    quantity = fields.Float('product_qty', digits=(32, 2))
    uom = fields.Char('uom')
    price_unit = fields.Float('price_unit', digits=(32, 2))
    taxes = fields.Char('taxes')
    subtotal = fields.Float('subtotal', digits=(32, 2))
    type_taxes = fields.Char('type_taxes')
    ex_in_clude = fields.Float('ex_in_clude', digits=(32, 2))
    total = fields.Float('total', digits=(32, 2))
    currency = fields.Char('currency')
    fiscalyear = fields.Char('fiscalyear')
    invoice_plan = fields.Char('invoice_plan')
    fin_lease = fields.Char('fin_lease')
    supplier_code = fields.Char('partner_code')
    supplier_name = fields.Char('partner_name')
    org_code = fields.Char('ou_code')
    org_name = fields.Char('ou_name')
    costcenter_code = fields.Char('costcenter_code')
    costcenter_name = fields.Char('costcenter_name')
    mission_name = fields.Char('mission_name')
    functional_area_code = fields.Char('functional_area_code')
    functional_area_name = fields.Char('functional_area_name')
    program_group_code = fields.Char('program_group_code')
    program_group_name = fields.Char('program_group_name')
    program_code = fields.Char('program_code')
    program_name = fields.Char('program_name')
    project_group_code = fields.Char('project_group_code')
    project_group_name = fields.Char('project_group_name')
    master_plan_code = fields.Char('master_plan_code')
    master_plan_name = fields.Char('master_plan_name')
    project_type_code = fields.Char('project_type_code')
    project_type_name = fields.Char('project_type_name')
    operation_code = fields.Char('operation_code')
    operation_name = fields.Char('operation_name')
    fund_type_code = fields.Char('fund_code')
    fund_type_name = fields.Char('fund_name')
    project_date_start = fields.Char('project_date_start')
    project_date_end = fields.Char('project_date_end')
    start_date_spending = fields.Char('start_spend')
    end_date_spending = fields.Char('end_spend')
    pm_code = fields.Char('pm_code')
    pm_name = fields.Char('pm_name')
    project_status = fields.Char('myp_status')
    sector_code = fields.Char('section_code')
    sector_name = fields.Char('section_name')
    subsector_code = fields.Char('subsector_code')
    subsector_name = fields.Char('subsector_name')
    division_code = fields.Char('division_code')
    division_name = fields.Char('division_name')
    section_program_code = fields.Char('section_code')
    section_program_name = fields.Char('section_name')
    project_c_code = fields.Char('project_c_code')
    project_c_name = fields.Char('project_c_name')
    pm_project_c_code = fields.Char('pm_project_c_code')
    pm_project_c_name = fields.Char('pm_project_c_name')
    po_status = fields.Char('po_status')


    def _get_sql_view(self):
        sql_view = """
    SELECT 
        ROW_NUMBER() over (order by pol.id) AS id,
        po.name as doc_number, 
        to_char(po.date_order, 'DD/MM/YYYY') as order_date, 
            pur_con.name as po_contract, 
            CASE
                WHEN pur_con.id is not null THEN pct.name
                ELSE po_ct.name
            END as po_contract_type,
            to_char(po.date_contract_start, 'DD/MM/YYYY') as po_contract_start_date,
            to_char(po.date_contract_end, 'DD/MM/YYYY') as po_contract_end_date, 
            pur_me.name as procurement_method, 
            (SELECT prt.name FROM purchase_request prt
                LEFT JOIN purchase_request_line prtl ON prtl.request_id = prt.id
                LEFT JOIN purchase_request_purchase_requisition_line_rel prpr ON prpr.purchase_request_line_id = prtl.id
                LEFT JOIN purchase_requisition_line prl ON prl.id = prpr.purchase_requisition_line_id
             WHERE prl.requisition_id = pur_re.id limit 1
            ) as pr_reference_doc,
            pur_re.name as pd_reference_doc,
            CAST(ROW_NUMBER() OVER(PARTITION BY po.name ORDER BY pol.id) AS Int) AS item,
            product.name_template as product, 
            'description' as description, 
            to_char(pol.date_planned, 'DD/MM/YYYY') as scheduled_date, 
            pcg.name as product_cat, aac.code as gl, aac.name as gl_name,
            ag.code as activity_group_code, ag.name as activity_group_name, 
            aa.code as activity_rpt_code, aa.name as activity_rpt_name,
            CASE 
                WHEN pol.project_id IS NOT NULL THEN 'project_base'
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN 'investment_construction'
                WHEN pol.section_id IS NOT NULL THEN 'unit_base'
                WHEN pol.invest_asset_id IS NOT NULL THEN 'invest_asset'
                ELSE null
            END as budget_view,
            CASE 
                WHEN pol.project_id IS NOT NULL THEN mpj.project_code
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN ricp.code
                WHEN pol.section_id IS NOT NULL THEN mst.section_code
                WHEN pol.invest_asset_id IS NOT NULL THEN inv_mst.section_code
                ELSE null
            END as budget_code,
            CASE 
                WHEN pol.project_id IS NOT NULL THEN mpj.project_name
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN ricp.name
                WHEN pol.section_id IS NOT NULL THEN mst.section_name
                WHEN pol.invest_asset_id IS NOT NULL THEN inv_mst.section_name
                ELSE null
            END as budget_name,
            mpj.fund_name as fund, 
            CASE
                WHEN pol.cost_control_id IS NOT NULL THEN CONCAT('[',cost_con.code,'] ',cost_con.name) 
                ELSE NULL
            END as job_order, 
            ROUND(pol.product_qty, 2) as quantity, uom.name as uom, 
            pol.price_unit,
            (SELECT STRING_AGG(tax.description, ', ') AS state_code FROM account_tax tax 
                 LEFT JOIN purchase_order_taxe pot ON pot.tax_id = tax.id
                 LEFT JOIN purchase_order_line pol2 ON pol.id = pot.ord_id
             WHERE pol2.id = pol.id
            ) AS taxes,
            ROUND(pol.product_qty*pol.price_unit, 2) as subtotal,
            CASE
                WHEN (SELECT taxs.price_include FROM account_tax taxs
                        LEFT JOIN purchase_order_taxe pots ON pots.tax_id = taxs.id
                        LEFT JOIN purchase_order_line pols2 ON pol.id = pots.ord_id
                     WHERE pols2.id = pol.id limit 1) = True THEN 'Inc-VAT'
                WHEN (SELECT taxs.price_include FROM account_tax taxs
                        LEFT JOIN purchase_order_taxe pots ON pots.tax_id = taxs.id
                        LEFT JOIN purchase_order_line pols2 ON pol.id = pots.ord_id
                     WHERE pols2.id = pol.id limit 1) IS NULL THEN NULL
                ELSE 'Exc-VAT'
            END as type_taxes,
            CASE
                WHEN (SELECT taxs.price_include FROM account_tax taxs
                        LEFT JOIN purchase_order_taxe pots ON pots.tax_id = taxs.id
                        LEFT JOIN purchase_order_line pols2 ON pol.id = pots.ord_id
                     WHERE pols2.id = pol.id limit 1) = True THEN ROUND(((pol.product_qty*pol.price_unit)*7)/107, 2)
                WHEN (SELECT taxs.price_include FROM account_tax taxs
                        LEFT JOIN purchase_order_taxe pots ON pots.tax_id = taxs.id
                        LEFT JOIN purchase_order_line pols2 ON pol.id = pots.ord_id
                     WHERE pols2.id = pol.id limit 1) != True THEN ROUND(((pol.product_qty*pol.price_unit)*7)/100, 2)
                ELSE 0.00
            END as ex_in_clude,
            CASE
                WHEN (SELECT taxs.price_include FROM account_tax taxs
                        LEFT JOIN purchase_order_taxe pots ON pots.tax_id = taxs.id
                        LEFT JOIN purchase_order_line pols2 ON pol.id = pots.ord_id
                     WHERE pols2.id = pol.id limit 1) = True THEN ROUND(pol.product_qty*pol.price_unit, 2)
                WHEN (SELECT taxs.price_include FROM account_tax taxs
                        LEFT JOIN purchase_order_taxe pots ON pots.tax_id = taxs.id
                        LEFT JOIN purchase_order_line pols2 ON pol.id = pots.ord_id
                     WHERE pols2.id = pol.id limit 1) IS NULL THEN ROUND(pol.product_qty*pol.price_unit, 2)
                ELSE ROUND(pol.product_qty*pol.price_unit + (((pol.product_qty*pol.price_unit)*7)/100), 2)
            END as total, 
            cur.name as currency, fis.name as fiscalyear,
            CASE 
                WHEN po.use_invoice_plan = True THEN 'X'
                ELSE ''
            END as invoice_plan,
            CASE 
                WHEN po.is_fin_lease = True THEN 'X'
                ELSE ''
            END as fin_lease,
            part.search_key as supplier_code, part.name as supplier_name, org.code as org_code, ou.code as org_name,
            mpj.costcenter_code, mpj.costcenter_name, 
            CASE 
                WHEN pol.project_id IS NOT NULL THEN mpj.mission
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN mis_pjc.name
                WHEN pol.section_id IS NOT NULL THEN mst.mission_code
                WHEN pol.invest_asset_id IS NOT NULL THEN inv_mst.mission_code
                ELSE null
            END as mission_name,
            mpj.functional_area_code, mpj.functional_area_name,
            mpj.program_group_code, mpj.program_group_name, mpj.program_code, mpj.program_name, 
            mpj.project_group_code, mpj.project_group_name, mpj.master_plan_code, mpj.master_plan_name, 
            mpj.project_type_code, mpj.project_type_name, mpj.operation_code, mpj.operation_name, 
            mpj.fund_code as fund_type_code, mpj.fund_name as fund_type_name, 
            to_char(res_pj.project_date_start, 'DD/MM/YYYY') as project_date_start, 
            to_char(res_pj.project_date_end, 'DD/MM/YYYY') as project_date_end, 
            to_char(res_pj.date_start, 'DD/MM/YYYY') as start_date_spending,
            to_char(res_pj.date_end, 'DD/MM/YYYY') as end_date_spending, 
            mpj.pm_code, mpj.pm_name, mpj.myp_status as project_status,
            mst.sector_code, mst.sector_name, mst.subsector_code, mst.subsector_name, mst.division_code, 
            mst.division_name, mst.section_code as section_program_code, mst.section_name as section_program_name,
            CASE
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN ricp.code
                ELSE null
            END as project_c_code,
            CASE
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN ricp.name
                ELSE null
            END as project_c_name,
            CASE
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN hr_emp.employee_code
                ELSE null
            END as pm_project_c_code,
            CASE
                WHEN pol.invest_construction_phase_id IS NOT NULL THEN CONCAT(hr_emp.first_name_th,' ',hr_emp.last_name_th)
                ELSE null
            END as pm_project_c_name,
            CASE 
                WHEN po.state = 'approved' THEN 'PO Released'
                WHEN po.state = 'confirmed' THEN 'Waiting to Release'
                WHEN po.state = 'done' THEN 'Done'
                ELSE NULL
            END as po_status
    FROM purchase_order po
        LEFT JOIN purchase_contract pur_con ON pur_con.id = po.contract_id
        LEFT JOIN purchase_contract_type po_ct ON po_ct.id = po.po_contract_type_id
        LEFT JOIN purchase_contract_type pct ON pct.id = pur_con.contract_type_id
        LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
        LEFT JOIN account_activity_group ag ON ag.id = pol.activity_group_id
        LEFT JOIN account_activity aa ON aa.id = pol.activity_rpt_id
        LEFT JOIN account_account aac ON aac.id = aa.account_id
        LEFT JOIN cost_control cost_con ON cost_con.id = pol.cost_control_id
        LEFT JOIN purchase_requisition pur_re ON pur_re.id = po.requisition_id
        LEFT JOIN purchase_method pur_me ON pur_me.id = pur_re.purchase_method_id
        LEFT JOIN product_product product ON product.id = pol.product_id
        LEFT JOIN product_uom uom ON uom.id = pol.product_uom
        LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
        LEFT JOIN product_category pcg ON pcg.id = pt.categ_id
        LEFT JOIN res_partner part ON part.id = po.partner_id
        LEFT JOIN operating_unit ou ON ou.id = po.operating_unit_id
        LEFT JOIN res_org org ON org.id = ou.org_id
        LEFT JOIN res_currency cur ON cur.id = po.currency_id
        LEFT JOIN res_invest_construction_phase ricp ON ricp.id = pol.invest_construction_phase_id
        LEFT JOIN res_invest_construction ric ON ric.id = pol.invest_construction_id
        LEFT JOIN res_mission mis_pjc ON mis_pjc.id = ric.mission_id
        LEFT JOIN issi_hr_employee_view hr_emp ON hr_emp.id = ric.pm_employee_id
        LEFT JOIN account_fiscalyear fis ON fis.id = pol.fiscalyear_id
        LEFT JOIN etl_issi_m_project mpj ON mpj.pb2_project_id = pol.project_id
        LEFT JOIN etl_issi_m_section mst ON mst.section_id = pol.section_id
        LEFT JOIN res_project res_pj ON res_pj.id = pol.project_id
        LEFT JOIN res_invest_asset res_inv ON res_inv.id = pol.invest_asset_id
        LEFT JOIN etl_issi_m_section inv_mst ON inv_mst.section_id = res_inv.owner_section_id
    WHERE po.state in ('approved','confirmed','done')
        and po.order_type = 'purchase_order'
    order by pol.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
        
  
