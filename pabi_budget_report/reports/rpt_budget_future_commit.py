# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from openerp.exceptions import ValidationError
from datetime import datetime 

REPORT_TYPES = [('all', 'All'),
                ('overall', 'Overall'),
                ('unit_base', 'Section'),
                ('project_base', 'Project'),
                ('invest_asset', 'Asset'),
                ('invest_construction', 'Construction'),
                ('personnel', 'Personnel')]
class RPTBudgetFutureCommit(models.TransientModel):
    _name = 'rpt.budget.future.commit'
    _inherit = 'report.budget.common.multi'
    
    
    report_type = fields.Selection(
        selection=lambda self: self._get_report_type(),
        string='Report Type',
        required=True,
        default='all'
    )
    date_report = fields.Date(
        string='Report Date',
        #default=lambda self: fields.Date.context_today(self),
        #required=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    results = fields.Many2many(
        'rpt.budget.future.commit.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    @api.model
    def _get_report_type(self):
        report_types = REPORT_TYPES
        if self._context.get('action_type', False) == 'my_budget_future_commit':
            report_types = [('all', 'All'),
                            ('unit_base', 'Section'),
                            ('project_base', 'Project'),
                            ('invest_asset', 'Asset'),
                            ('invest_construction', 'Construction')]
        return report_types
    
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        section_ids = []
        project_ids = []
        invest_construction_phase_ids = []
        invest_asset_ids = []
            
        date_report = self.date_report
        Result = self.env['rpt.budget.future.commit.line']
        
        dom += [('fiscalyear_id', '=', self.fiscalyear_id.id)]
        
        if self.chartfield_ids:
            chartfield = self.chartfield_ids
            
            section_ids = self._get_chartfield_ids(chartfield, 'sc:')
            project_ids = self._get_chartfield_ids(chartfield, 'pj:')
            invest_construction_phase_ids = self._get_chartfield_ids(chartfield, 'cp:')
            invest_asset_ids = self._get_chartfield_ids(chartfield, 'ia:')
            
        if self.report_type != 'all':
            dom += [('budget_view', '=', self.report_type)]
        if self.date_report:
            dom += [('order_date', '=', str((datetime.strptime(str(self.date_report), '%Y-%m-%d')).strftime("%d/%m/%Y")))]
        if self.org_id:
            dom += [('operating_unit_id.org_id', '=', self.org_id.id)]
        if self.sector_id:
            dom += [('sector_code', '=', self.sector_id.code)]
        if self.subsector_id:
            dom += [('subsector_code', '=', self.subsector_id.code)]
        if self.division_id:
            dom += [('division_code', '=', self.division_id.code)]
        if self.section_id:
            section_ids.append(self.section_id.id)
        if self.section_program_id:
            dom += [('section_program_id', '=', self.section_program_id.id)]
        if self.invest_asset_id:
            invest_asset_ids.append(self.invest_asset_id.id)
        if self.activity_group_id:
            dom += [('activity_group_id', '=', self.activity_group_id.id)]
        if self.activity_id:
            dom += [('activity_rpt_id', '=', self.activity_id.id)]
        if self.functional_area_id:
            dom += [('functional_area_id', '=', self.functional_area_id.id)]
        if self.program_group_id:
            dom += [('program_group_id', '=', self.program_group_id.id)]
        if self.program_id:
            dom += [('program_id', '=', self.program_id.id)]
        if self.project_group_id:
            dom += [('project_group_id', '=', self.project_group_id.id)]
        if self.project_id:
            project_ids.append(self.project_id.id)
        if self.invest_construction_id:
            dom += [('invest_construction_id', '=', self.invest_construction_id.id)]
        if self.purchase_id:
            dom += [('purchase_id', '=', self.purchase_id.id)]
            
        if len(section_ids) > 0:
            dom += [('section_id', 'in', section_ids)]
        if len(project_ids) > 0:
            dom += [('project_id', 'in', project_ids)]
        if len(invest_construction_phase_ids) > 0:
            dom += [('invest_construction_phase_id', 'in', invest_construction_phase_ids)]
        if len(invest_asset_ids) > 0:
            dom += [('invest_asset_id', 'in', invest_asset_ids)]

        self.results = Result.search(dom)
    
    
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
        data['parameters']['org'] = self.org_id and self.org_id.operating_unit_id.name or ''
        data['parameters']['po_document'] = self.purchase_id and self.purchase_id.name or ''
        data['parameters']['order_date'] = self.date_report and str((datetime.strptime(str(self.date_report), '%Y-%m-%d')).strftime("%d/%m/%Y")) or ''
        data['parameters']['budget_overview'] = ''#self.chart_view
        data['parameters']['budget_method'] = ''#self.budget_method
        data['parameters']['run_by'] = self.create_uid.partner_id.name
        data['parameters']['run_date'] = str((datetime.strptime(str(self.create_date), '%Y-%m-%d %H:%M:%S')).strftime("%d/%m/%Y"))
        
        report_ids = 'pabi_budget_report.rpt_budget_future_commit_jasper_report'
        
        return super(RPTBudgetFutureCommit, self).run_jasper_report(data, report_ids)
    
        
        
class RPTBudgetFutureCommitLine(models.Model):
    _name = 'rpt.budget.future.commit.line'
    #_auto = False
    
    #id = fields.Integer('ID')
    order_date = fields.Char('order_date')
    po_contract_start_date = fields.Char('po_contract_start_date')
    po_contract_end_date = fields.Char('po_contract_end_date')
    item = fields.Integer('item')
    scheduled_date = fields.Char('scheduled_date')
    budget_view = fields.Char('budget_view')
    budget_code = fields.Char('budget_code')
    budget_name = fields.Char('budget_name')
    fund = fields.Char('fund')
    taxes = fields.Char('taxes')
    subtotal = fields.Float('subtotal', digits=(32, 2))
    subtotal_th = fields.Float('subtotal th', digits=(32, 2))
    type_taxes = fields.Char('type_taxes')
    ex_in_clude = fields.Float('ex_in_clude', digits=(32, 2))
    total = fields.Float('total', digits=(32, 2))
    invoice_plan = fields.Char('invoice_plan')
    fin_lease = fields.Char('fin_lease')
    mission_name = fields.Char('mission_name')
    costcenter_code = fields.Char('costcenter_code')
    costcenter_name = fields.Char('costcenter_name')
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
    fund_type_code = fields.Char('fund_type_code')
    fund_type_name = fields.Char('fund_type_name')
    pm_code = fields.Char('pm_code')
    pm_name = fields.Char('pm_name')
    project_status = fields.Char('project_status')
    project_date_start = fields.Char('project_date_start')
    project_date_end = fields.Char('project_date_end')
    start_date_spending = fields.Char('start_spend')
    end_date_spending = fields.Char('end_spend')
    sector_code = fields.Char('sector_code')
    sector_name = fields.Char('sector_name')
    subsector_code = fields.Char('subsector_code')
    subsector_name = fields.Char('subsector_name')
    division_code = fields.Char('division_code')
    division_name = fields.Char('division_name')
    section_program_code = fields.Char('section_program_code')
    section_program_name = fields.Char('section_program_name')
    pm_project_c_code = fields.Char('PM Project-C code')
    pm_project_c_name = fields.Char('PM Project-C Name')
    po_status = fields.Char('po_status')
    
    activity_group_id = fields.Many2one('account.activity.group')
    activity_rpt_id = fields.Many2one('account.activity')
    contract_id = fields.Many2one('purchase.contract')
    currency_id = fields.Many2one('res.currency')
    fiscalyear_id = fields.Many2one('account.fiscalyear')
    invest_construction_phase_id = fields.Many2one('res.invest.construction.phase')
    operating_unit_id = fields.Many2one('operating.unit')
    partner_id = fields.Many2one('res.partner')
    po_contract_type_id = fields.Many2one('purchase.contract.type')
    product_categ_id = fields.Many2one('product.category')
    product_id = fields.Many2one('product.product')
    purchase_id = fields.Many2one('purchase.order')
    purchase_line_id = fields.Many2one('purchase.order.line')
    purchase_method_id = fields.Many2one('purchase.method')
    request_id = fields.Many2one('purchase.request')
    requisition_id = fields.Many2one('purchase.requisition')
    uom_id = fields.Many2one('product.uom')
    section_id = fields.Many2one('res.section')
    section_program_id = fields.Many2one('res.section.program')
    invest_asset_id = fields.Many2one('res.invest.asset')
    functional_area_id = fields.Many2one('res.functional.area')
    program_group_id = fields.Many2one('res.program.group')
    program_id = fields.Many2one('res.program')
    project_group_id = fields.Many2one('res.project.group')
    project_id = fields.Many2one('res.project')
    invest_construction_id = fields.Many2one('res.invest.construction')
    

    """def _get_sql_view(self):
        sql_view = "
    SELECT 
        ROW_NUMBER() over (order by pol.id) AS id,
        to_char(po.date_order, 'DD/MM/YYYY') as order_date, 
        to_char(po.date_contract_start, 'DD/MM/YYYY') as po_contract_start_date,
        to_char(po.date_contract_end, 'DD/MM/YYYY') as po_contract_end_date, 
        CAST(ROW_NUMBER() OVER(PARTITION BY po.name ORDER BY pol.id) AS Int) AS item,
        to_char(pol.date_planned, 'DD/MM/YYYY') as scheduled_date,
        CASE 
            WHEN pol.project_id IS NOT NULL THEN 'project_base'
            WHEN pol.invest_construction_phase_id IS NOT NULL THEN 'invest_construction'
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
        (SELECT STRING_AGG(tax.description, ', ') AS state_code FROM account_tax tax 
             LEFT JOIN purchase_order_taxe pot ON pot.tax_id = tax.id
             LEFT JOIN purchase_order_line pol2 ON pol.id = pot.ord_id
         WHERE pol2.id = pol.id
        ) AS taxes,
        ROUND(pol.product_qty*pol.price_unit, 2) as subtotal,
        ROUND((pol.product_qty*pol.price_unit)*
        (CASE
            WHEN cur.name = 'THB' THEN 1
            WHEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                 WHERE cur_r.currency_id = cur.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1) IS NULL 
             THEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                 WHERE cur_r.currency_id = cur.id and CAST(po.date_order AS DATE) > CAST(cur_r.name AS DATE) order by cur_r.name DESC limit 1)
            ELSE (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                 WHERE cur_r.currency_id = cur.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1)
        END), 2) as subtotal_th,
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
                 WHERE pols2.id = pol.id limit 1) is null THEN 0.00
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
        CASE 
            WHEN po.use_invoice_plan = True THEN 'X'
            ELSE ''
        END as invoice_plan,
        CASE 
            WHEN po.is_fin_lease = True THEN 'X'
            ELSE ''
        END as fin_lease,
        CASE 
            WHEN pol.project_id IS NOT NULL THEN mpj.mission
            WHEN pol.invest_construction_phase_id IS NOT NULL THEN mis_pjc.name
            WHEN pol.section_id IS NOT NULL THEN mst.mission_code
            WHEN pol.invest_asset_id IS NOT NULL THEN inv_mst.mission_code
            ELSE null
        END as mission_name,
        mpj.costcenter_code, mpj.costcenter_name, mpj.functional_area_code, mpj.functional_area_name,
        mpj.program_group_code, mpj.program_group_name, mpj.program_code, mpj.program_name, 
        mpj.project_group_code, mpj.project_group_name, mpj.master_plan_code, mpj.master_plan_name, 
        mpj.project_type_code, mpj.project_type_name, mpj.operation_code, mpj.operation_name, 
        mpj.fund_code as fund_type_code, mpj.fund_name as fund_type_name, 
        mpj.pm_code, mpj.pm_name, mpj.myp_status as project_status,
        to_char(res_pj.project_date_start, 'DD/MM/YYYY') as project_date_start, 
        to_char(res_pj.project_date_end, 'DD/MM/YYYY') as project_date_end, 
        to_char(res_pj.date_start, 'DD/MM/YYYY') as start_date_spending,
        to_char(res_pj.date_end, 'DD/MM/YYYY') as end_date_spending,
        mst.sector_code, mst.sector_name, mst.subsector_code, mst.subsector_name, mst.division_code, 
        mst.division_name, mst.section_code as section_program_code, mst.section_name as section_program_name,
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
        END as po_status,
        CASE
            WHEN pur_con.id is not null THEN pur_con.contract_type_id
            ELSE po.po_contract_type_id
        END as po_contract_type_id,
        pol.activity_group_id, pol.activity_rpt_id, po.contract_id, po.currency_id, pol.fiscalyear_id, pol.invest_construction_phase_id,
        po.operating_unit_id, po.partner_id,
        pt.categ_id as product_categ_id, pol.product_id, po.id as purchase_id, pol.id as purchase_line_id, pur_re.purchase_method_id,
        (SELECT prt.id FROM purchase_request prt
            LEFT JOIN purchase_request_line prtl ON prtl.request_id = prt.id
            LEFT JOIN purchase_request_purchase_requisition_line_rel prpr ON prpr.purchase_request_line_id = prtl.id
            LEFT JOIN purchase_requisition_line prl ON prl.id = prpr.purchase_requisition_line_id
         WHERE prl.requisition_id = pur_re.id limit 1
        ) as request_id,
        po.requisition_id, pol.product_uom as uom_id, pol.section_id, pol.section_program_id, pol.invest_asset_id,
        mpj.pb2_functional_area_id as functional_area_id,
        mpj.pb2_program_group_id as program_group_id,
        mpj.pb2_program_id as program_id,
        mpj.pb2_project_group_id as project_group_id,
        mpj.pb2_project_id as project_id,
        pol.invest_construction_id
    FROM purchase_order po
        LEFT JOIN purchase_contract pur_con ON pur_con.id = po.contract_id
        LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
        LEFT JOIN res_currency cur ON cur.id = po.currency_id
        LEFT JOIN purchase_requisition pur_re ON pur_re.id = po.requisition_id
        LEFT JOIN purchase_method pur_me ON pur_me.id = pur_re.purchase_method_id
        LEFT JOIN product_product product ON product.id = pol.product_id
        LEFT JOIN product_template pt ON pt.id = product.product_tmpl_id
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
        "
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(CREATE OR REPLACE VIEW %s AS (%s)"
                   % (self._table, self._get_sql_view()))
    """
  
