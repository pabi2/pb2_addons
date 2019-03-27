# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


REFERENCE_SELECT = [
    ('res.section', 'Section'),
    ('res.project', 'Project'),
    ('res.invest.asset', 'Invest Asset'),
    ('res.invest.construction.phase', 'Invest Construction Phase'),
]


class AssetRegisterView(models.AbstractModel):
    """ Contrast to normal view, this will be used as mock temp table only """
    _name = 'asset.register.view'
    _inherit = 'account.asset'

    asset_id = fields.Many2one(
        'account.asset',
        string='Asset ID',
    )
    budget = fields.Reference(
        REFERENCE_SELECT,
        string='Budget',
    )
    owner_budget = fields.Reference(
        REFERENCE_SELECT,
        string='Owner Budget',
    )
    depreciation = fields.Float(
        # compute='_compute_depreciation',
        string='Depreciation',
    )
    accumulated_cf = fields.Float(
        # compute='_compute_accumulated_cf',
        string='Accumulated Depreciation',
    )
    accumulated_bf = fields.Float(
        # compute='_compute_accumulated_bf',
        string='Accumulated Depreciation Before',
    )
    budget_type = fields.Char(
        string='Budget Type',
    )
    purchase_before_current = fields.Float(
        string='Purchase Value Before Current FY',
    )
    purchase_current = fields.Float(
        string='Purchase Value Current FY',
    )
    net_book_value = fields.Float(
        string='Net Book Value',
    )
    account_code = fields.Char(
        string='Account Code',
    )
    account_name = fields.Char(
        string='Account Name',
    )


class AssetRegisterReport(models.TransientModel):
    _name = 'asset.register.report'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        readonly=True,
        default='filter_date',
    )
    asset_status_ids = fields.Many2many(
        'account.asset.status',
        string='Asset Status',
    )
    asset_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    asset_ids = fields.Many2many(
        'account.asset',
        string='Asset Code',
    )
    count_asset = fields.Integer(
        compute='_compute_count_asset',
        string='Asset Count',
    )
    asset_profile_ids = fields.Many2many(
        'account.asset.profile',
        string='Asset Profile',
        required=False,
    )
    responsible_person_ids = fields.Many2many(
        'res.users',
        string='Responsible Person',
    )
    building_ids = fields.Many2many(
        'res.building',
        string='Building',
    )
    floor_ids = fields.Many2many(
        'res.floor',
        string='Floor',
    )
    room_ids = fields.Many2many(
        'res.room',
        string='Room',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
    )
    asset_state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Running'),
         ('close', 'Close'),
         ('removed', 'Removed')],
        string='Asset State',
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Account Code',
    )
    costcenter_ids = fields.Many2many(
        'res.costcenter',
        string='Cost Center',
    )
    division_ids = fields.Many2many(
        'res.division',
        string='Division',
    )
    sector_ids = fields.Many2many(
        'res.sector',
        string='Sector',
    )
    subsector_ids = fields.Many2many(
        'res.subsector',
        string='Subsector',
    )
    current_year = fields.Many2one(
        'account.fiscalyear',
        string='Current Year',
        default=lambda self: self._get_fiscalyear(),
    )
    # Note: report setting
    accum_depre_account_type = fields.Many2one(
        'account.account.type',
        string='Account Type for Accum.Depre.',
        required=True,
        help="Define account type for accumulated depreciation account, "
        "to be used in report query SQL."
    )
    depre_account_type = fields.Many2one(
        'account.account.type',
        string='Account Type for Depre.',
        required=True,
        help="Define account type for depreciation account, "
        "to be used in report query SQL."
    )

    # More fileter
    budget_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    budget = fields.Many2many(
        'chartfield.view',
        'asset_register_chartfield_rel',
        'wizard_id', 'chartfield_id',
        string='Source Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    count_budget = fields.Integer(
        compute='_compute_count_budget',
        string='Budget Count',
    )
    owner_budget_filter = fields.Text(
        string='Filter',
        help="More filter. You can use complex search with comma and between.",
    )
    owner_budget = fields.Many2many(
        'chartfield.view',
        'asset_register_owner_chartfield_rel',
        'wizard_id', 'chartfield_id',
        string='Owner Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
    )
    count_owner_budget = fields.Integer(
        compute='_compute_count_budget',
        string='Budget Count',
    )
    asset_status = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive')],
        string='Asset Status',
        default='active',
    )
    results = fields.Many2many(
        'asset.register.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    @api.multi
    @api.depends('asset_ids')
    def _compute_count_asset(self):
        for rec in self:
            rec.count_asset = len(rec.asset_ids)

    @api.multi
    @api.depends('budget', 'owner_budget')
    def _compute_count_budget(self):
        for rec in self:
            rec.count_budget = len(rec.budget)
            rec.count_owner_budget = len(rec.owner_budget)
    # @api.onchange('building_id')
    # def _onchange_building_id(self):
    #     self.floor_id = False
    #     self.room_id = False
    #
    # @api.onchange('floor_id')
    # def _onchange_floor_id(self):
    #     self.room_id = False

    @api.model
    def _domain_to_where_str(self, domain):
        """ Helper Function for better performance """
        where_dom = [" %s %s %s " % (x[0], x[1], isinstance(x[2], basestring)
                     and "'%s'" % x[2] or x[2]) for x in domain]
        where_str = 'and'.join(where_dom)
        return where_str

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
        if self.responsible_person_ids:
            dom += [('responsible_user_id', 'in',
                     tuple(self.responsible_person_ids.ids + [0]))]
        if self.org_ids:
            dom += [('org_id', 'in', tuple(self.org_ids.ids + [0]))]
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
        if self.costcenter_ids:
            dom += [('owner_costcenter_id', 'in',
                    tuple(self.costcenter_ids.ids + [0]))]
        if self.division_ids:
            dom += [('owner_division_id', 'in',
                    tuple(self.division_ids.ids + [0]))]
        if self.sector_ids:
            dom += [('owner_sector_id', 'in',
                    tuple(self.sector_ids.ids + [0]))]
        if self.subsector_ids:
            dom += [('owner_subsector_id', 'in',
                    tuple(self.subsector_ids.ids + [0]))]
        if self.asset_state:
            dom += [('state', '=', self.asset_state)]
        if self.building_ids:
            dom += [('building_id', 'in', tuple(self.building_ids.ids + [0]))]
        if self.floor_ids:
            dom += [('floor_id', 'in', tuple(self.floor_ids.ids + [0]))]
        if self.room_ids:
            dom += [('room_id', 'in', tuple(self.room_ids.ids + [0]))]
        if self.asset_status:
            dom += [('active', '=', True if (self.asset_status == 'active') else False)]
            
        # Prepare fixed params
        date_start = False
        date_end = False
        if self.filter == 'filter_date':
            date_start = self.date_start
            date_end = self.date_end
        if self.filter == 'filter_period':
            date_start = self.period_start_id.date_start
            date_end = self.period_end_id.date_stop
        if not date_start or not date_end:
            raise ValidationError(_('Please provide from and to dates.'))
        accum_depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.accum_depre_account_type.id)]).ids
        depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.depre_account_type.id)]).ids
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
                (select a.purchase_value - coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulated account
                 and ml.date <= %s -- date end
                 and asset_id = a.id) net_book_value,
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
                (select coalesce(sum(debit-credit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- depreciation account
                 and ml.date between %s and %s
                 and asset_id = a.id) depreciation,
                -- accumulated_cf
                (select coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulated account
                 and ml.date <= %s -- date end
                 and asset_id = a.id) accumulated_cf,
                -- accumulated_bf
                (select coalesce(sum(credit-debit), 0.0)
                 from account_move_line ml
                 where account_id in %s  -- accumulatedp account
                 and ml.date < %s -- date start
                 and asset_id = a.id) accumulated_bf
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
        """ + where_str + 'order by asset.account_code, asset.code',
                         (tuple(accum_depre_account_ids), date_end,
                          tuple(depre_account_ids), date_start, date_end,
                          tuple(accum_depre_account_ids), date_end,
                          tuple(accum_depre_account_ids), date_start))
        results = self._cr.dictfetchall()
        ReportLine = self.env['asset.register.view']
        for line in results:
            self.results += ReportLine.new(line)
        return True

    # @api.multi
    # def action_get_report(self):
    #     action = self.env.ref(
    #         'pabi_account_report.action_asset_register_report_form')
    #     return super(AssetRegisterReport, self).action_get_report()

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
