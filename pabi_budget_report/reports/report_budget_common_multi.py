# -*- coding: utf-8 -*-
# import openerp
from openerp import models, fields, api, tools, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import ChartField
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError
import time

REPORT_TYPES = [('all', 'All'),
                ('overall', 'Overall'),
                ('unit_base', 'Section'),
                ('project_base', 'Project'),
                ('invest_asset', 'Asset'),
                ('invest_construction', 'Construction'),
                ('personnel', 'Personnel')]

REPORT_GROUPBY = {
    'all': [],
    'unit_base': ['section_id', 'activity_group_id',
                  'charge_type', 'activity_id', 'budget_method'],
    'project_base': ['project_id', 'activity_group_id',
                     'charge_type', 'activity_id', 'budget_method'],
    'invest_asset': ['org_id', 'invest_asset_id', 'budget_method'],
    'invest_construction': ['org_id', 'invest_construction_id',
                            'invest_construction_phase_id', 'budget_method'],
    'personnel': ['org_id', 'personnel_costcenter_id',
                  'activity_group_id', 'activity_id', 'budget_method']
}

CHARTFIELDS_TYPE = {'sc:': 1000000, 'pj:': 2000000, 'cp:': 3000000, 'ia:': 4000000, 'pc:':5000000}

@job(default_channel='root.budget_report')
def get_report_job(session, model_name, res_id, lang=False):
    try:
        # Update context
        ctx = session.context.copy()
        if lang:
            ctx.update({'lang': lang})
        out_file, out_name = session.pool[model_name].get_report(
            session.cr, session.uid, [res_id], ctx)
        # Make attachment and link ot job queue
        job_uuid = session.context.get('job_uuid')
        job = session.env['queue.job'].search([('uuid', '=', job_uuid)],
                                              limit=1)
        # Get init time
        date_created = fields.Datetime.from_string(job.date_created)
        ts = fields.Datetime.context_timestamp(job, date_created)
        init_time = ts.strftime('%d/%m/%Y %H:%M:%S')
        # Create output report place holder
        desc = 'INIT: %s\n> UUID: %s' % (init_time, job_uuid)
        session.env['ir.attachment'].create({
            'name': out_name,
            'datas': out_file,
            'datas_fname': out_name,
            'res_model': 'queue.job',
            'res_id': job.id,
            'type': 'binary',
            'parent_id': session.env.ref('pabi_utils.dir_spool_report').id,
            'description': desc,
            'user_id': job.user_id.id,
        })
        # Result Description
        result = _('Successfully created excel report : %s') % out_name
        return result
    except Exception, e:
        raise FailedJobError(e)

class ReportBudgetCommonMulti(ChartField, models.AbstractModel):
    _name = 'report.budget.common.multi'
    _inherit = 'xlsx.report'

    budget_commit_type = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('actual', 'Actual'),
         ],
        string='Budget Commit Type',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    report_type = fields.Selection(
        selection=lambda self: self._get_report_type(),
        string='Report Type',
        required=True,
        default='all'
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,  # Overwrite as requried field.
        default=lambda self: self._get_fiscalyear(),
    )
    # ------------ SEARCH ------------
    # For All
    chartfield_id = fields.Many2one(
        'chartfield.view',
        string='Budget',
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budgets',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    section_program_id = fields.Many2one(
        'res.section.program',
        string='Section Program',
    )
    # For: Overall
    org_id = fields.Many2one(
        'res.org',
        string='Orgs',
    )
    # For unit_base
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
    )
    # For project_base and invest_construction
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Project (C)',
    )
    # For unit_base and invest_asset
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Investment Asset',
    )
    # For project_base
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area'
    )
    program_group_id = fields.Many2one(
        'res.program.group',
        string='Program Group'
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program'
    )
    project_group_id = fields.Many2one(
        'res.project.group',
        string='Project Group'
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project'
    )
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter'
    )
    # Group By
    group_by_chartfield_id = fields.Boolean(
        string='Group By - Budget',
        default=False,
    )
    group_by_section_id = fields.Boolean(
        string='Group By - Section',
        default=False,
    )
    group_by_project_id = fields.Boolean(
        string='Group By - Project',
        default=False,
    )
    group_by_personnel_costcenter_id = fields.Boolean(
        string='Group By - Personnel Budget',
        default=False,
    )
    group_by_activity_group_id = fields.Boolean(
        string='Group By - Activity Group',
        default=False,
    )
    group_by_charge_type = fields.Boolean(
        string='Group By - Charge Type',
        default=False,
    )
    group_by_activity_id = fields.Boolean(
        string='Group By - Activity',
        default=False,
    )
    group_by_invest_asset_id = fields.Boolean(
        string='Group By - Asset',
        default=False,
    )
    group_by_org_id = fields.Boolean(
        string='Group By - Org',
        default=False,
    )
    group_by_invest_construction_id = fields.Boolean(
        string='Group By - Project C',
        default=False,
    )
    group_by_invest_construction_phase_id = fields.Boolean(
        string='Group By - Project Phase',
        default=False,
    )
    group_by_budget_method = fields.Boolean(
        string='Group By - Budget Method',
        default=False,
    )
    # group_by_personnel_budget_id = fields.Boolean(
    #     string='Group By - Personnel Budget',
    #     default=False,
    # )
    # For my budget report
    section_ids = fields.Many2many(
        'res.section',
        string='Section',
        #domain=lambda self: self._get_domain_section(),
    )
    project_ids = fields.Many2many(
        'res.project',
        string='Project',
        #domain=lambda self: self._get_domain_project(),
    )
    action_type = fields.Selection(
        [('budget_overview_report', 'Budget Overview Report'),
         ('my_budget_report', 'My Budget Report')],
        string='Action Type',
    )
    xlsx_report = fields.Boolean(
        string='xlsx report',
        default=False,
    )
    analytic_report = fields.Boolean(
        string='analytic report',
        default=False,
    )
    jasper_report = fields.Boolean(
        string='jasper report',
        default=False,
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    chart_view = fields.Selection(
        [('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
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
    
    @api.model
    def _get_fiscalyear(self):
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', self.env.user.company_id.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        return fiscalyear
    

    @api.model
    def _get_report_type(self):
        report_types = REPORT_TYPES
        if self._context.get('action_type', False) == 'my_budget_report':
            report_types = [('all', 'All'),
                            ('unit_base', 'Section'),
                            ('project_base', 'Project')]
        return report_types
    
    
    @api.onchange('report_type')
    def _onchange_report_type(self):
        # For budget overview report
        self.charge_type = False
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False
        self.invest_asset_id = False
        self.activity_group_id = False
        self.activity_id = False
        self.functional_area_id = False
        self.program_group_id = False
        self.program_id = False
        self.project_group_id = False
        self.project_id = False
        self.invest_construction_id = False
        self.chartfield_id = False
        self.chartfield_ids = False
        self.section_program_id = False
        # For my budget report
        self.section_ids = False
        self.project_ids = False

    @api.onchange('org_id')
    def _onchange_org_id(self):
        if self.org_id:
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False

    @api.onchange('sector_id')
    def _onchange_sector_id(self):
        if self.sector_id:
            self.org_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False

    @api.onchange('subsector_id')
    def _onchange_subsector_id(self):
        if self.subsector_id:
            self.org_id = False
            self.sector_id = False
            self.division_id = False
            self.section_id = False

    @api.onchange('division_id')
    def _onchange_division_id(self):
        if self.division_id:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.section_id = False

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False

    @api.onchange('functional_area_id')
    def _onchange_functional_area_id(self):
        if self.functional_area_id:
            self.program_group_id = False
            self.program_id = False
            self.project_group_id = False
            self.project_id = False

    @api.onchange('program_group_id')
    def _onchange_program_group_id(self):
        if self.program_group_id:
            self.functional_area_id = False
            self.program_id = False
            self.project_group_id = False
            self.project_id = False

    @api.onchange('program_id')
    def _onchange_program_id(self):
        if self.program_id:
            self.functional_area_id = False
            self.program_group_id = False
            self.project_group_id = False
            self.project_id = False

    @api.onchange('project_group_id')
    def _onchange_project_group_id(self):
        if self.project_group_id:
            self.functional_area_id = False
            self.program_group_id = False
            self.program_id = False
            self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.functional_area_id = False
            self.program_group_id = False
            self.program_id = False
            self.project_group_id = False

    @api.onchange('activity_id')
    def _onchange_activity_id(self):
        if self.activity_id:
            self.activity_group_id = False

    @api.onchange('activity_group_id')
    def _onchange_activity_group_id(self):
        if self.activity_group_id:
            self.activity_id = False
            
    
    @api.onchange('xlsx_report','async_process')
    def _onchange_report_xlsx_print(self):
        if self.xlsx_report or self.async_process:
            self.analytic_report = False
            self.jasper_report = False
        
    @api.onchange('analytic_report')
    def _onchange_report_analytic_print(self):
        if self.analytic_report:
            self.xlsx_report = False
            self.jasper_report = False
            self.async_process = False
            self.to_csv = False
        
    @api.onchange('jasper_report')
    def _onchange_report_jasper_print(self):
        if self.jasper_report:
            self.xlsx_report = False
            self.analytic_report = False
            self.async_process = False
            self.to_csv = False
    
    @api.multi
    def _get_chartfield_ids(self, chartfield, type):
        chartfield_id = []
        
        chartfield_ids = chartfield.filtered(lambda l: l.type == type).ids
        
        for chart in chartfield_ids:
            chartfield_id.append(chart-CHARTFIELDS_TYPE[type])
            
        return chartfield_id
        
    
    @api.multi
    def get_jasper_report(self):
        self.ensure_one()
        Export = self.env['export.xlsx.template']
        Attachment = self.env['ir.attachment']
        template = []
        # By default, use template by model
        if self.specific_template:
            template = self.env.ref(self.specific_template, [])
        else:
            template = Attachment.search([('res_model', '=', self._name)])
        if len(template) != 1:
            raise ValidationError(
                _('No one template selected for "%s"') % self._name)
        return Export._export_template(
            template, self._name, self.id,
            to_csv=self.to_csv,
            csv_delimiter=self.csv_delimiter,
            csv_extension=self.csv_extension,
            csv_quote=self.csv_quote)
            
            
    @api.multi
    def action_get_report(self):
        self.ensure_one()
        # Enqueue
        if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Excel Report - %s' % (self._name, )
            uuid = get_report_job.delay(
                session, self._name, self.id, description=description,
                lang=session.context.get('lang', False))
            job = Job.search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_utils.xlsx_report')
            self.write({'state': 'get', 'uuid': uuid})
        else:
            out_file, out_name = self.get_report()
            self.write({'state': 'get', 'data': out_file, 'name': out_name})
            
        view_id = self.env.ref('pabi_budget_report.view_budget_common_show_uuid_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(view_id, 'form')],
            'target': 'new',
        }
    
    
    @api.multi
    def run_report(self):
        raise ValidationError(_('Not implemented.'))
    
    @api.multi
    def run_jasper_report(self, data, report_ids):
        self.ensure_one()
        # Enqueue
        """if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Excel Report - %s' % (self._name, )
            uuid = get_report_job.delay(
                session, self._name, self.id, description=description,
                lang=session.context.get('lang', False))
            job = Job.search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_budget_multi_report.jasper_report')
            self.write({'state': 'get', 'uuid': uuid})
        
        #else:
            #print '\n ELSE'
            #out_file, out_name = self.get_report()
            #self.write({'state': 'get', 'data': out_file, 'name': out_name})
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }"""
        
        report_name = self.env.ref(report_ids).report_name
        print '\n report_name'+str(report_name)
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
        }
            
            

            