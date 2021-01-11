# -*- coding: utf-8 -*-
from openerp import models, fields, api

class JasperReportGlProject(models.TransientModel):
    _name = 'jasper.report.gl.project'
    _inherit = 'report.account.common'

    account_type_id = fields.Many2one(
        'account.account.type',
        string='Account Type',
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Account Code',
    )
    line_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    chartfield_ids = fields.Many2many(
        'chartfield.view',
        string='Budget',
        domain=['|',('active', '=', False),('active', '=', True),('model', '!=', 'res.personnel.costcenter')],
    )
    chart_view = fields.Selection(
        [('personnel', 'Personnel'),
         ('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
        required=False,
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    invest_asset_ids = fields.Many2many(
        'res.invest.asset',
        string='Investment Asset',
    )
    section_ids = fields.Many2many(
        'res.section',
        string='Section',
    )
    fund_ids = fields.Many2many(
        'res.fund',
        string='Source of Fund',
    )
    project_ids = fields.Many2many(
        'res.project',
        string='Project',
    )
    invest_construction_ids = fields.Many2many(
        'res.invest.construction',
        string='Project (C)',
    )
    activity_group_ids = fields.Many2many(
        'account.activity.group',
        string='Activity Group',
    )
    activity_ids = fields.Many2many(
        'account.activity',
        string='Activity',
    )
    count_chartfield = fields.Integer(
        compute='_compute_count_chartfield',
        string='Budget Count',
    )
    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
    )
    results = fields.Many2many(
        'account.move.line',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    filter = fields.Selection(
        selection_add=[('filter_clearing_date', 'Clearing date')],
    )
    cleaning_date_start = fields.Date(
        string='Start Date',
    )
    cleaning_date_end = fields.Date(
        string='End Date',
    )
    
    line_filter_job = fields.Text(
        string='Job',
        help="More filter Job. You can use complex search with comma and between.",
    )

    job_order_ids = fields.Many2many(
        'cost.control',
        string='Job Order',
    )
    count_job_order = fields.Integer(
        compute='_compute_job_order',
        string='Job Order Count',
    )

    @api.onchange('chart_view')
    def _onchange_chart_view(self):
        self.org_ids = False
        self.invest_asset_ids = False
        self.section_ids = False
        self.fund_ids = False
        self.project_ids = False
        self.invest_construction_ids = False
        
    @api.multi
    @api.depends('job_order_ids')
    def _compute_job_order(self):
        for rec in self:
            rec.count_job_order = len(rec.job_order_ids)    

    @api.multi
    @api.depends('chartfield_ids')
    def _compute_count_chartfield(self):
        for rec in self:
            rec.count_chartfield = len(rec.chartfield_ids)

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move.line']
        dom = []
        if self.account_type_id:
            dom += [(" aa.user_type = {} ".format(self.account_type_id.id))]
        if self.account_ids:
            dom += [(' aml.account_id in ({}) '.\
                     format(','.join(map(str, (self.account_ids.ids)))))]
        if self.activity_group_ids:
            dom += [(' aml.activity_group_id in ({}) '.\
                     format(','.join(map(str, (self.activity_group_ids.ids)))))]
        if self.activity_ids:
            dom += [(' aml.activity_id in ({}) '.\
                     format(','.join(map(str, (self.activity_ids.ids)))))]
        if self.charge_type:
            dom += [(" aml.charge_type = '{}' ".format(self.charge_type))]
        # Filter chart view
#         if self.chart_view == 'personnel':
#             dom += [('org_id', '!=', False)]
#         elif self.chart_view == 'invest_asset':
#             dom += [('invest_asset_id', '!=', False)]
#         elif self.chart_view == 'unit_base':
#             dom += [('section_id', '!=', False)]
#         elif self.chart_view == 'project_base':
#             dom += [('project_id', '!=', False)]
#         elif self.chart_view == 'invest_construction':
#             dom += [('invest_construction_id', '!=', False)]
        if self.org_ids:
            dom += [(' aml.org_id in ({}) '.\
                     format(','.join(map(str, (self.org_ids.ids)))))]
        if self.invest_asset_ids:
            dom += [(' aml.invest_asset_id in ({}) '.\
                     format(','.join(map(str, (self.invest_asset_ids.ids)))))]
        if self.section_ids:
            dom += [(' aml.section_id in ({}) '.\
                     format(','.join(map(str, (self.section_ids.ids)))))]
        if self.fund_ids:
            dom += [(' aml.fund_id in ({}) '.\
                     format(','.join(map(str, (self.fund_ids.ids)))))]
        if self.project_ids:
            dom += [(' aml.project_id in ({}) '.\
                     format(','.join(map(str, (self.project_ids.ids)))))]
        if self.invest_construction_ids:
            dom += [(' aml.invest_construction_id in ({}) '.\
                     format(','.join(map(str, (self.invest_construction_ids.ids)))))]
        if self.job_order_ids:
            dom += [(' aml.cost_control_id in ({}) '.\
                     format(','.join(map(str, (self.job_order_ids.ids)))))]
        if self.chartfield_ids:
            # map beetween chartfield_id with chartfield type
            chartfields = [('section_id', 'sc:'),
                           ('project_id', 'pj:'),
                           ('invest_construction_phase_id', 'cp:'),
                           ('invest_asset_id', 'ia:'),
                           ('personnel_costcenter_id', 'pc:')]
            where_str = ''
            res_ids = []
            for chartfield_id, chartfield_type in chartfields:
                chartfield_ids = self.chartfield_ids.filtered(
                    lambda l: l.type == chartfield_type).mapped('res_id')
                if chartfield_ids:
                    if where_str:
                        where_str += ' or '
                    where_str += chartfield_id + ' in %s'
                    res_ids.append(tuple(chartfield_ids))
            if res_ids:
                sql = "select id from account_move_line where " + where_str
                self._cr.execute(sql, res_ids)
                aml_id = map(lambda l: l[0], self._cr.fetchall())
                dom += [(' aml.id in ({}) '.format(','.join(map(str, (aml_id)))))]
        # Filter date
        if self.fiscalyear_start_id:
            date_start = self.fiscalyear_start_id.date_start
        if self.fiscalyear_end_id:
            date_end = self.fiscalyear_end_id.date_stop
        if self.period_start_id:
            date_start = self.period_start_id.date_start
        if self.period_end_id:
            date_end = self.period_end_id.date_stop
        if self.date_start:
            date_start = self.date_start
        if self.date_end:
            date_end = self.date_end
        cleaning_date_start = self.cleaning_date_start
        cleaning_date_end = self.cleaning_date_end
            
        return dom,date_start,date_end,cleaning_date_start,cleaning_date_end

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
    
    @api.onchange('line_filter_job')
    def _onchange_line_filter_job(self):
        self.job_order_ids = []
        Cost = self.env['cost.control']
        dom = []
        n=0
        if self.line_filter_job:
            codes = self.line_filter_job.replace(' ','').replace('\n',',').replace(',,',',').replace(',\n','').split(',')
            if '' in codes:
                codes.remove('')
            codes = [x.strip() for x in codes]
            for rec in codes:
                n += 1
                if rec != '':
                    if n != len(codes):
                        dom.append('|')
                    dom.append(('code', 'ilike', rec))
            self.job_order_ids = Cost.search(dom, order='id')

    @api.onchange('account_type_id')
    def _onchange_account_type(self):
        self.account_ids = False
        account_type_id = self.account_type_id.id
        domain = [('type', '!=', 'view')]
        if account_type_id:
            domain = [('user_type', '=', account_type_id)]
        return {'domain': {'account_ids': domain}}
    
    @api.multi
    def start_report(self):
        self.ensure_one()
        dom,date_start,date_end,cleaning_date_start,cleaning_date_end \
        = self._compute_results()
        params = {}
        params['date_start'] = date_start
        params['date_end'] = date_end
        params['condition'] = ' where ' +  ('and'.join(map(str, dom)))
        return { 
            'type': 'ir.actions.report.xml',
            'report_name': 'report_asset_register',
            'datas': params,
        }