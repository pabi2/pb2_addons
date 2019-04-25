# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from openerp.exceptions import ValidationError
from datetime import datetime 


class RPTBudgetCommit(models.TransientModel):
    _name = 'rpt.budget.commit'
    _inherit = 'report.budget.common.multi'
    
    
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
    )
    results = fields.Many2many(
        'rpt.budget.commit.line',
        string='Results',
        compute='_compute_results',
    )
    
    
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        section_ids = []
        project_ids = []
        invest_construction_phase_ids = []
        invest_asset_ids = []
        
        Result = self.env['rpt.budget.commit.line']
        
        """if self.chartfield_ids:
            chartfield = self.chartfield_ids
            
            section_ids = self._get_chartfield_ids(chartfield, 'sc:')
            project_ids = self._get_chartfield_ids(chartfield, 'pj:')
            invest_construction_phase_ids = self._get_chartfield_ids(chartfield, 'cp:')
            invest_asset_ids = self._get_chartfield_ids(chartfield, 'ia:')
          
        if self.report_type != 'all':
            dom += [('budget_view', '=', self.report_type)]
        if self.date_report:
            dom += [('order_date', '=', str((datetime.strptime(str(self.date_report), '%Y-%m-%d')).strftime("%d/%m/%Y")))]
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
        """
        self.results = Result.search(dom, limit=5)
    
    
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
        data['parameters']['report_type'] = ''
        data['parameters']['fiscal_year'] = self.fiscalyear_id.name or ''
        data['parameters']['org'] = self.org_id and self.org_id.operating_unit_id.name or ''
        data['parameters']['po_document'] = self.purchase_id and self.purchase_id.name or ''
        data['parameters']['order_date'] = ''
        data['parameters']['budget_overview'] = self.chart_view or ''
        data['parameters']['budget_method'] = self.budget_method or ''
        data['parameters']['run_by'] = self.create_uid.partner_id.name or ''
        data['parameters']['run_date'] = str((datetime.strptime(str(self.create_date), '%Y-%m-%d %H:%M:%S')).strftime("%d/%m/%Y"))
        
        report_ids = 'pabi_budget_report.rpt_budget_commit_jasper_report'
        
        return super(RPTBudgetCommit, self).run_jasper_report(data, report_ids)
    

    
     
       
class RPTBudgetCommitLine(models.Model):
    _name = 'rpt.budget.commit.line'
    _auto = False
    
    id = fields.Integer('ID')
    budget_commit_type = fields.Char('budget_commit_type')
    charge_type = fields.Char('charge_type')
    budget_method = fields.Char('budget_method')
    doctype = fields.Char('doctype')
    chart_view = fields.Char('chart_view')
    fisyear = fields.Char('fisyear')
    period = fields.Char('period')
    document = fields.Char('document')
    detail = fields.Char('detail')
    activity_group = fields.Char('activity_group')
    activity_group_name = fields.Char('activity_group_name')
    activity = fields.Char('activity')
    activity_name = fields.Char('activity_name')
    section = fields.Char('section')
    section_name = fields.Char('section_name')
    project = fields.Char('project')
    project_name = fields.Char('project_name')
    org = fields.Char('org')
    org_name = fields.Char('org_name')
    costcenter = fields.Char('costcenter')
    costcenter_name = fields.Char('costcenter_name')
    purchase_line_id = fields.Many2one('purchase.order.line','purchase_line_id')
    purchase_request_line_id = fields.Many2one('purchase.request.line','purchase_request_line_id')
    expense_line_id = fields.Many2one('hr.expense.line','expense_line_id')
    sale_line_id = fields.Many2one('sale.order.line','sale_line_id')
    amount = fields.Float('amount')
    date_doc = fields.Date('date_doc')
    posting_date = fields.Char('posting_date')
    

    def _get_sql_view(self):
        sql_view = """
        SELECT 
            com.id, com.budget_commit_type, com.charge_type, com.budget_method, com.doctype, com.chart_view, com.fisyear, com.period, com.document,
            com.detail, com.activity_group, com.activity_group_name, com.activity, com.activity_name, com.section, com.section_name, com.project,
            com.project_name, com.org, com.org_name, com.costcenter, com.costcenter_name, com.purchase_line_id, com.purchase_request_line_id,
            com.expense_line_id, com.sale_line_id, com.amount, com.date_doc,
            CASE
                WHEN com.doctype = 'purchase_request' THEN to_char(pr.date_approve, 'DD/MM/YYYY')
                WHEN com.doctype = 'purchase_order' THEN to_char(po.date_order, 'DD/MM/YYYY')
                WHEN com.doctype = 'employee_expense' THEN to_char(ex.date, 'DD/MM/YYYY')
                ELSE ''
            END AS posting_date,
            CASE
                WHEN com.chart_view = 'invest_construction' THEN bgcon.code
                WHEN com.chart_view = 'invest_asset' THEN bgasset.code
                WHEN com.chart_view = 'project_base' THEN prj.project_code
                WHEN com.chart_view = 'unit_base' THEN sec2.section_code
                WHEN com.chart_view = 'personnel' THEN budper.code
                ELSE ''::character varying
            END AS source_budget_code,
            CASE
                WHEN com.chart_view = 'invest_construction' THEN bgcon.phase_name
                WHEN com.chart_view = 'invest_asset' THEN bgasset.name
                WHEN com.chart_view = 'project_base' THEN prj.project_name::character varying
                WHEN com.chart_view = 'unit_base' THEN sec2.section_name::character varying
                WHEN com.chart_view = 'personnel' THEN budper.name
                ELSE ''
            END AS source_budget_name,
        FROM issi_budget_commit_view com
            LEFT JOIn purchase_order_line pol ON pol.id = com.purchase_line_id
            LEFT JOIn purchase_order po ON po.id = pol.order_id
            LEFT JOIn purchase_request_line prl ON prl.id = com.purchase_request_line_id
            LEFT JOIn purchase_request pr ON pr.id = prl.request_id
            LEFT JOIn hr_expense_line exl ON exl.id = com.expense_line_id
            LEFT JOIN hr_expense_expense ex ON ex.id = exl.expense_id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
        

