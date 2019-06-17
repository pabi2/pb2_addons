# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


REFERENCE_SELECT = [
    ('res.section', 'Section'),
    ('res.project', 'Project'),
    ('res.invest.asset', 'Invest Asset'),
    ('res.invest.construction.phase', 'Invest Construction Phase'),
]

class AssetRegisterReport(models.TransientModel):
    _name = 'asset.estimate.report'
    _inherit = 'report.account.common'

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
        'asset_register_owner_chartfield_rel',
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
        'asset_register_chartfield_rel',
        'wizard_id', 'chartfield_id',
        string='Source Budget',
        domain=[('model', '!=', 'res.personnel.costcenter')],
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
    results = fields.Many2many(
        'asset.register.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )
    
    @api.multi
    def _compute_results(self):
        self.ensure_one()
        dom = []
        if self.fiscalyear_start_id:
            dom += [('date', '>=', self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('date', '<=', self.fiscalyear_end_id.date_stop)] 
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
        date_start = self.fiscalyear_start_id.date_start
        date_end = self.fiscalyear_end_id.date_stop
        
        if not date_start or not date_end:
            raise ValidationError(_('Please provide from and to dates.'))
        
        accum_depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.accum_depre_account_type.id)]).ids
        depre_account_ids = self.env['account.account'].search(
            [('user_type', '=', self.depre_account_type.id)]).ids
        where_str = self._domain_to_where_str(dom)
        if where_str:
            where_str = 'where ' + where_str
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