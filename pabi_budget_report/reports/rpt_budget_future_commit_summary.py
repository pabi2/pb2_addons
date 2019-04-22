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
            dom += [('sector_id', '=', self.sector_id.id)]
        if self.subsector_id:
            dom += [('subsector_id', '=', self.subsector_id.id)]
        if self.division_id:
            dom += [('division_id', '=', self.division_id.id)]
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
        
        report_ids = 'pabi_budget_report.rpt_budget_future_commit_summary_jasper_report'
        
        return super(RPTBudgetFutureCommitSummary, self).run_jasper_report(data, report_ids)
    
        
class RPTBudgetFutureCommitSummaryLine(models.Model):
    _name = 'rpt.budget.future.commit.summary.line'
    _auto = False
    
    id = fields.Integer('ID')
    subtotal = fields.Float('subtotal', digits=(32, 2))
    po_commit = fields.Float('po_commit', digits=(32, 2))
    po_actual = fields.Float('po_actual', digits=(32, 2))
    #remaining = fields.Float('remaining', digits=(32, 2))
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
    #sector_id = fields.Many2one('res.sector')
    #subsector_id = fields.Many2one('res.subsector')
    #division_id = fields.Many2one('res.division')
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
            SELECT ROW_NUMBER() over (order by po.id) AS id, po.name,
                SUM(fc.subtotal_th) as subtotal,
                (SELECT SUM(sum_com.amount) FROM issi_budget_summary_commit_view sum_com WHERE sum_com.document = po.name 
                    AND sum_com.fisyear = fis.name AND sum_com.budget_commit_type in ('po_commit') 
                    AND sum_com.budget_method in ('expense'))
                as po_commit,
                (SELECT SUM(sum_act.amount) FROM issi_budget_summary_actual_view sum_act WHERE sum_act.ref_document = po.name 
                    AND sum_act.fisyear = fis.name AND sum_act.charge_type in ('external') AND sum_act.document_ref in ('account_invoice', 'stock_picking')
                    AND sum_act.budget_method in ('expense') AND sum_act.ref_document not like 'EX%')
                as po_actual,
                fc.budget_view, fc.budget_code, fc.budget_name, fc.contract_id, fc.fiscalyear_id, fc.invest_construction_phase_id, 
                fc.operating_unit_id, fc.sector_code, fc.sector_name, fc.subsector_code, fc.subsector_name, fc.division_code, 
                fc.division_name, fc.section_id, fc.section_program_id, fc.invest_asset_id, fc.functional_area_id, fc.program_group_id, 
                fc.program_id, fc.project_group_id, fc.project_id, fc.invest_construction_id, fc.purchase_id
            FROM rpt_budget_future_commit_line fc
                LEFT JOIN purchase_order po ON po.id = fc.purchase_id
                LEFT JOIN account_fiscalyear fis ON fis.id = fc.fiscalyear_id
            GROUP BY po.id, po.name, fc.purchase_id, fis.name, fc.budget_view, fc.budget_code, fc.budget_name, fc.contract_id, fc.fiscalyear_id, 
                fc.invest_construction_phase_id, fc.operating_unit_id, fc.sector_code, fc.sector_name, fc.subsector_code, 
                fc.subsector_name, fc.division_code, fc.division_name, fc.section_id, fc.section_program_id, fc.invest_asset_id, 
                fc.functional_area_id, fc.program_group_id, fc.program_id, fc.project_group_id, fc.project_id, fc.invest_construction_id
        """
        
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))
