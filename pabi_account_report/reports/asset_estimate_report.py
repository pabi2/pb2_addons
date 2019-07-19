# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime
from __builtin__ import str
import time

REFERENCE_SELECT = [
    ('res.section', 'Section'),
    ('res.project', 'Project'),
    ('res.invest.asset', 'Invest Asset'),
    ('res.invest.construction.phase', 'Invest Construction Phase'),
]

class AssetRegisterReport(models.TransientModel):
    _name = 'asset.estimate.report'
    _inherit = 'report.account.common'

    number =  fields.Selection(
        [(1, '1 ปี'),
         (2, '2 ปี'),
         (3, '3 ปี'),
         (4, '4 ปี'),
         (5, '5 ปี'),],
        string='Number of year',
        default=5,
        require=True,
    )
    period_year_id = fields.Many2one(
        'account.fiscalyear',
        string='Start Year',
        default=lambda self: self._get_fiscalyear(),
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Account Code',
    )
    asset_state = fields.Many2many(
        'xlsx.report.status',
        string='Asset State',
        domain=[('location', '=', 'asset.register.view')],
        default=lambda self: self.env['xlsx.report.status'].search([('location', '=', 'asset.register.view'),('status', 'in', ['draft', 'open', 'close'])]),
    )
    asset_profile_ids = fields.Many2many(
        'account.asset.profile',
        string='Asset Profile',
        required=False,
    )
    asset_status_ids = fields.Many2many(
        'account.asset.status',
        string='Asset Status',
    ) 
    asset_active = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive')],
        string='Asset Active',
        default='active',
    )
    asset_ids = fields.Many2many(
        'account.asset',
        string='Asset Code',
    )
    # Note: Asset filter
    count_asset = fields.Integer(
        compute='_compute_count_asset',
        string='Asset Count',
    )
    asset_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    
    # Note: budget filter
    count_budget = fields.Integer(
        compute='_compute_count_budget',
        string='Budget Count',
    )
    budget_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    owner_budget_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    owner_budget = fields.Many2many(
        'chartfield.view',
        'asset_estimate_owner_chartfield_rel',
        'wizard_id', 'chartfield_id',
        string='Owner Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    count_owner_budget = fields.Integer(
        compute='_compute_count_budget',
        string='Budget Count',
    )
    budget = fields.Many2many(
        'chartfield.view',
        'asset_estimate_chartfield_rel',
        'wizard_id', 'chartfield_id',
        string='Source Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    # Note: report setting
    accum_depre_account_type = fields.Many2one(
        'account.account.type',
        string='Account Type for Accum.Depre.',
        required=True,
        default=lambda self: self.env['account.account.type'].search([('name','=','Accumulated Depreciation')]),
        help="Define account type for accumulated depreciation account, "
        "to be used in report query SQL."
    )
    depre_account_type = fields.Many2one(
        'account.account.type',
        string='Account Type for Depre.',
        required=True,
        default=lambda self: self.env['account.account.type'].search([('name','=','Depreciation')]),
        help="Define account type for depreciation account, "
        "to be used in report query SQL."
        
    )
    results = fields.Many2many(
        'asset.register.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        where_str = 'and'.join(where_dom)
        return where_str
    
    def cal_year(self,date,vals):
        date = date.split('-') #[0]: year [1]: months [2]:Date
        date[0] = str(int(date[0])+vals)
        return "-".join(date)
        
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        # Prepare DOM to filter assets
        if self.asset_ids:
            dom += [('id', 'in', tuple(self.asset_ids.ids + [0]))]
        if self.asset_profile_ids:
            dom += [('profile_id', 'in',
                    tuple(self.asset_profile_ids.ids + [0]))]
        if self.asset_status_ids:
            dom += [('status', 'in',
                    tuple(self.asset_status_ids.ids + [0]))]
        if self.account_ids:
            dom += [('account_asset_id', 'in',
                    tuple(self.account_ids.ids + [0]))]
        if self.budget:
            dom_budget = \
                ["%s,%s" % ((x.model).encode('utf-8'), x.res_id)
                 for x in self.budget]
            dom += [('budget', 'in', tuple(dom_budget + ['0']))]
        if self.owner_budget:
            dom_owner = \
                ["%s,%s" % ((x.model).encode('utf-8'), x.res_id)
                 for x in self.owner_budget]
            dom += [('owner_budget', 'in', tuple(dom_owner + ['0']))]
        if self.asset_state:
            res, state_name = [], self.asset_state
            for state in self.asset_state:
                state_name = self.env['xlsx.report.status'].search([('id', '=', state.id)])
                res += [str(state_name.status)]
            if len(self.asset_state) == 1 : dom += [('state', '=', str(state_name.status))]
            else: dom += [('state', 'in', tuple(res))]
        if self.asset_active:
            dom += [('active', '=', True if (self.asset_active == 'active') else False)]

        # Prepare fixed params       
        date_start = self.fiscalyear_start_id.date_start    #'201x-10-01'
        date_end = self.fiscalyear_start_id.date_stop  #'201x-09-30'
        date_dep_start = self.period_year_id.date_start
        date_dep_end = self.period_year_id.date_stop
        
        if self.date_start:
            dom += [('date_start', '<=', self.date_end)]
            
            
        if not date_start or not date_end:
            raise ValidationError(_('Please provide from and to dates.'))
        accum_depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.accum_depre_account_type.id)]).ids
        depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.depre_account_type.id)]).ids
        
        whr_depreciation = ""
        for x in range(0,self.number):
            if x == 0: #1 year
                pass
            elif x==1: #2 year
                date_start1 = self.cal_year(date_dep_start,x)
                date_end1 = self.cal_year(date_dep_end,x)
                whr_depreciation +=  """-- depreciation1
                (select coalesce(sum(line.amount), 0.0)
                 from account_asset_line line
                 left join account_asset asset on line.asset_id = asset.id
                 where line.line_date between '%s' and '%s' 
                 and asset.code = a.code) depreciation1,""" % (date_start1, date_end1,)
            elif x==2: #3 year  
                date_start2 = self.cal_year(date_dep_start,x)
                date_end2 = self.cal_year(date_dep_end,x)  
                whr_depreciation +=  """-- depreciation2
                    (select coalesce(sum(line.amount), 0.0)
                 from account_asset_line line
                 left join account_asset asset on line.asset_id = asset.id
                 where line.line_date between '%s' and '%s' 
                 and asset.code = a.code) depreciation2,""" % (date_start2, date_end2,)
            elif x==3: #4 year
                date_start3 = self.cal_year(date_dep_start,x)
                date_end3 = self.cal_year(date_dep_end,x)
                whr_depreciation +=  """-- depreciation3
                    (select coalesce(sum(line.amount), 0.0)
                 from account_asset_line line
                 left join account_asset asset on line.asset_id = asset.id
                 where line.line_date between '%s' and '%s'
                 and asset.code = a.code) depreciation3,""" % (date_start3, date_end3,)
            elif x==4: #5 year    
                date_start4 = self.cal_year(date_dep_start,+4)
                date_end4 = self.cal_year(date_dep_end,+4)
                whr_depreciation +=  """-- depreciation4
                    (select coalesce(sum(line.amount), 0.0)
                 from account_asset_line line
                 left join account_asset asset on line.asset_id = asset.id
                 where line.line_date between '%s' and '%s' 
                 and asset.code = a.code) depreciation4,""" % (date_start4, date_end4,)
                    
        date_bef_start = self.cal_year(date_start,-1)
        #date_bef_end  = self.cal_year(date_end,-1)
        date_bef_end  = self.cal_year(date_dep_end,-1)
        
        where_str = self._domain_to_where_str(dom)
        if where_str:
            where_str = 'where ' + where_str 
        self._cr.execute("""
            select *
            from (
                select a.*, a.id asset_id, aap.account_asset_id,
                aa.code as account_code, aa.name as account_name,
                -- purchase_bf_current
                case when date_part('year', a.date_start+92) !=
                 date_part('year', CURRENT_DATE+92) then a.purchase_value
                 else null end as purchase_before_current,
                -- purchase_current
                case when date_part('year', a.date_start+92) =
                 date_part('year', CURRENT_DATE+92) then a.purchase_value
                 else null end as purchase_current,
                -- net_book_value
                /*(select a.purchase_value - coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulated account
                 and ml.date <= %s -- date end
                 and asset_id = a.id) net_book_value,*/
                -- budget_type
                case when a.section_id is not null then 'Section'
                     when a.project_id is not null then 'Project'
                     when a.invest_asset_id is not null then 'Invest Asset'
                     when a.invest_construction_phase_id is not null
                        then 'Invest Construction Phase'
                    else null end as budget_type,
                -- budget
                case when a.section_id is not null then
                        concat('res.section,', a.section_id)
                     when a.project_id is not null then
                        concat('res.project,', a.project_id)
                     when a.invest_asset_id is not null then
                        concat('res.invest.asset,', a.invest_asset_id)
                     when a.invest_construction_phase_id is not null then
                        concat('res.invest.construction.phase,',
                               a.invest_construction_phase_id)
                     else null end as budget,
                -- owner_budget
                case when a.owner_section_id is not null then
                        concat('res.section,', a.owner_section_id)
                     when a.owner_project_id is not null then
                        concat('res.project,', a.owner_project_id)
                     when a.owner_invest_asset_id is not null then
                        concat('res.invest.asset,', a.owner_invest_asset_id)
                     when a.owner_invest_construction_phase_id is not null
                        then concat('res.invest.construction.phase,',
                                     a.owner_invest_construction_phase_id)
                     else null end as owner_budget,
                -- owner_costcenter
                case when a.owner_section_id is not null then
                        rs.costcenter_id
                     when a.owner_project_id is not null then
                        rp.costcenter_id
                     when a.owner_invest_asset_id is not null then
                        ria.costcenter_id
                     when a.owner_invest_construction_phase_id is not null then
                        ricp.costcenter_id
                     else null end as owner_costcenter_id,
                -- owner_division
                case when a.owner_section_id is not null then
                        rs.division_id
                     else null end as owner_division_id,
                -- owner_sector
                case when a.owner_section_id is not null then
                        rs.sector_id
                     else null end as owner_sector_id,
                -- owner_subsector
                case when a.owner_section_id is not null then
                        rs.subsector_id
                     else null end as owner_subsector_id,
                -- depreciation
                (select coalesce(sum(line.amount), 0.0)
                 from account_asset_line line
                 left join account_asset asset on line.asset_id = asset.id
                 where line.line_date between %s and %s 
                 and asset.code = a.code and line.type = 'depreciate') depreciation,
                """+ whr_depreciation +"""
                -- accumulated_cf
                (select coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulated account
                 and ml.date <= %s -- date end
                 and asset_id = a.id) accumulated_cf,
                -- accumulated_bf
                (select coalesce(sum(line.amount), 0.0)
                 from account_asset_line line
                 left join account_asset asset on line.asset_id = asset.id
                 where line.line_date between %s and %s 
                 and asset.id = a.id and line.type = 'depreciate') accumulated_bf
            from
            account_asset a
            left join account_asset_profile aap on a.profile_id = aap.id
            left join res_section rs on a.owner_section_id = rs.id
            left join res_project rp on a.owner_project_id = rp.id
            left join res_invest_asset ria on a.owner_invest_asset_id = ria.id
            left join res_invest_construction_phase ricp on
            a.owner_invest_construction_phase_id = ricp.id
            left join account_account aa on aap.account_asset_id = aa.id
            ) asset
        """ + where_str + 'order by asset.account_code, asset.code ',
                         (tuple(accum_depre_account_ids), date_end,
                          #tuple(depre_account_ids), 
                          date_dep_start, date_dep_end,
                          tuple(accum_depre_account_ids), date_end,
                          date_bef_start, date_bef_end)
            )   
        
        results = self._cr.dictfetchall()
        ReportLine = self.env['asset.register.view']
        for line in results:
            self.results += ReportLine.new(line)
        return True
            
    @api.multi
    @api.depends('asset_ids')
    def _compute_count_asset(self):
        for rec in self:
            rec.count_asset = len(rec.asset_ids)
            
    @api.onchange('asset_filter')
    def _onchange_asset_filter(self):
        self.asset_ids = []
        Asset = self.env['account.asset']
        dom = []
        if self.asset_filter:
            codes = self.asset_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.asset_ids = Asset.search(dom, order='id')
            
    @api.multi
    @api.depends('budget', 'owner_budget')
    def _compute_count_budget(self):
        for rec in self:
            rec.count_budget = len(rec.budget)
            rec.count_owner_budget = len(rec.owner_budget)

    @api.onchange('budget_filter')
    def _onchange_budget_filter(self):
        self.budget = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.budget_filter:
            codes = self.budget_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.budget = Chartfield.search(dom, order='id')     
            
    @api.onchange('owner_budget_filter')
    def _onchange_owner_budget_filter(self):
        self.budget = []
        Chartfield = self.env['chartfield.view']
        dom = []
        if self.owner_budget_filter:
            codes = self.owner_budget_filter.split('\n')
            codes = [x.strip() for x in codes]
            codes = ','.join(codes)
            dom.append(('code', 'ilike', codes))
            self.owner_budget = Chartfield.search(dom, order='id')              
            
class AssetRegisterView(models.AbstractModel):
    """ Add depreciation of 5 years  """
    _inherit = 'asset.register.view'
    
    depreciation1 = fields.Float(
        # compute='_compute_depreciation',
        string='Next 1 year of Depreciation',
    )
    depreciation2 = fields.Float(
        # compute='_compute_depreciation',
        string='Next 2 year of Depreciation',
    )
    depreciation3 = fields.Float(
        # compute='_compute_depreciation',
        string='Next 3 year of Depreciation',
    )
    depreciation4 = fields.Float(
        # compute='_compute_depreciation',
        string='Next 4 year of Depreciation',
    )