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


class RPTBudgetFutureCommitSummary(models.TransientModel):
    _name = 'rpt.budget.future.commit.summary'
    _inherit = 'report.budget.common.multi'
    
    
    report_type = fields.Selection(
        selection=lambda self: self._get_report_type(),
        string='Report Type',
        required=True,
        default='all'
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    results = fields.Many2many(
        'rpt.budget.future.commit.summary.line',
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
        
        Result = self.env['rpt.budget.future.commit.summary.line']
        
        if self.chartfield_ids:
            chartfield = self.chartfield_ids
            
            section_ids = self._get_chartfield_ids(chartfield, 'sc:')
            project_ids = self._get_chartfield_ids(chartfield, 'pj:')
            invest_construction_phase_ids = self._get_chartfield_ids(chartfield, 'cp:')
            invest_asset_ids = self._get_chartfield_ids(chartfield, 'ia:')
            
        if self.report_type != 'all':
            dom += [('budget_view', '=', self.report_type)]
        if self.fiscalyear_id:
            dom += [('fiscalyear_id', '=', self.fiscalyear_id.id)]
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

        self.results = Result.search(dom, limit=3)
    
    
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
        data['parameters']['order_date'] = ''#self.date_report and str((datetime.strptime(str(self.date_report), '%Y-%m-%d')).strftime("%d/%m/%Y")) or ''
        data['parameters']['run_by'] = self.create_uid.partner_id.name
        data['parameters']['run_date'] = str((datetime.strptime(str(self.create_date), '%Y-%m-%d %H:%M:%S')).strftime("%d/%m/%Y"))
        
        report_ids = 'pabi_budget_report.rpt_budget_future_commit_summary_jasper_report'
        
        return super(RPTBudgetFutureCommitSummary, self).run_jasper_report(data, report_ids)
    
        
class RPTBudgetFutureCommitSummaryLine(models.Model):
    _name = 'rpt.budget.future.commit.summary.line'
    _auto = False
    
    id = fields.Integer('ID')
    subtotal = fields.Float('subtotal', digits=(32, 2))
    po_commit = fields.Float('po_commit', digits=(32, 2))
    po_actual = fields.Float('po_actual', digits=(32, 2))
    remaining = fields.Float('remaining', digits=(32, 2))
    budget_view = fields.Char('budget_view')
    budget_code = fields.Char('budget_code')
    budget_name = fields.Char('budget_name')
    sector_code = fields.Char('sector_code')
    sector_name = fields.Char('sector_name')
    subsector_code = fields.Char('subsector_code')
    subsector_name = fields.Char('subsector_name')
    division_code = fields.Char('division_code')
    division_name = fields.Char('division_name')
    
    contract_id = fields.Many2one('purchase.contract')
    fiscalyear_id = fields.Many2one('account.fiscalyear')
    invest_construction_phase_id = fields.Many2one('res.invest.construction.phase')
    operating_unit_id = fields.Many2one('operating.unit')
    section_id = fields.Many2one('res.section')
    section_program_id = fields.Many2one('res.section.program')
    invest_asset_id = fields.Many2one('res.invest.asset')
    functional_area_id = fields.Many2one('res.functional.area')
    program_group_id = fields.Many2one('res.program.group')
    program_id = fields.Many2one('res.program')
    project_group_id = fields.Many2one('res.project.group')
    project_id = fields.Many2one('res.project')
    invest_construction_id = fields.Many2one('res.invest.construction')
    purchase_id = fields.Many2one('purchase.order')
    
    
    def _get_sql_view(self):
        sql_view = """
         SELECT 
        ROW_NUMBER() over (order by pol.order_id) AS id,
        SUM(ROUND((pol.product_qty*pol.price_unit)*
        (CASE
            WHEN cur.name = 'THB' THEN 1
             WHEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                 WHERE cur_r.currency_id = cur.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1) IS NULL 
             THEN (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
                 WHERE cur_r.currency_id = cur.id and CAST(po.date_order AS DATE) > CAST(cur_r.name AS DATE) order by cur_r.name DESC limit 1)
            ELSE (SELECT cur_r.rate_input FROM res_currency_rate cur_r 
             WHERE cur_r.currency_id = cur.id and CAST(po.date_order AS DATE) = CAST(cur_r.name AS DATE) limit 1)
        END), 2)) as subtotal,
        sum(sum_com.amount) as po_commit, sum(sum_act.amount) as po_actual, sum_act.budget_view,
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
        po.contract_id, pol.fiscalyear_id, pol.invest_construction_phase_id,
        po.operating_unit_id, pol.sector_id, pol.subsector_id, pol.division_id, pol.section_id, pol.section_program_id, 
        pol.invest_asset_id, pol.functional_area_id, pol.program_group_id, pol.program_id, pol.project_group_id, pol.project_id, 
        pol.invest_construction_id, pol.order_id as purchase_id
    FROM purchase_order po
        LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
        LEFT JOIN res_currency cur ON cur.id = po.currency_id
        LEFT JOIN etl_issi_m_project mpj ON mpj.pb2_project_id = pol.project_id
        LEFT JOIN etl_issi_m_section mst ON mst.section_id = pol.section_id
        LEFT JOIN res_invest_construction_phase ricp ON ricp.id = pol.invest_construction_phase_id
        LEFT JOIN res_invest_asset res_inv ON res_inv.id = pol.invest_asset_id
        LEFT JOIN etl_issi_m_section inv_mst ON inv_mst.section_id = res_inv.owner_section_id
        INNER JOIN issi_budget_summary_commit_view sum_com ON sum_com.document = po.name
        INNER JOIN issi_budget_summary_actual_view sum_act ON sum_act.ref_document = po.name
    WHERE sum_com.budget_commit_type in ('po_commit') AND sum_com.budget_method in ('expense')
        AND sum_act.charge_type in ('external') 
        AND sum_act.budget_method in ('expense') AND sum_act.ref_document not like 'EX%'
    GROUP BY sum_com.fisyear, sum_com.document, sum_act.budget_view,
        po.contract_id, pol.fiscalyear_id, pol.invest_construction_phase_id,
        po.operating_unit_id, pol.sector_id, pol.subsector_id, pol.division_id, pol.section_id, pol.section_program_id, 
        pol.invest_asset_id, pol.functional_area_id, pol.program_group_id, pol.program_id, pol.project_group_id, pol.project_id, 
        pol.invest_construction_id, pol.order_id, mpj.project_code, ricp.code, mst.section_code, inv_mst.section_code,
        mpj.project_name, ricp.name, mst.section_name, inv_mst.section_name
        """
        
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
