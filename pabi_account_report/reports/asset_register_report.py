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


class AssetRegisterReport(models.TransientModel):
    _name = 'asset.register.report'
    _inherit = 'report.account.common'

    filter = fields.Selection(
        [('filter_date', 'Dates'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_period',
    )
    asset_status_ids = fields.Many2many(
        'account.asset.status',
        string='Asset Status',
        required=True,
    )
    asset_ids = fields.Many2many(
        'account.asset',
        string='Asset Code',
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
    building_id = fields.Many2one(
        'res.building',
        string='Building',
    )
    floor_id = fields.Many2one(
        'res.floor',
        string='Floor',
    )
    room_id = fields.Many2one(
        'res.building',
        string='Room',
    )
    org_ids = fields.Many2many(
        'res.org',
        string='Org',
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
        Result = self.env['asset.register.view']
        dom = []
        # Prepare DOM to filter assets
        if self.asset_ids:
            dom += [('id', 'in', tuple(self.asset_ids.ids))]
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
        if self.building_id:
            dom += [('building_id', '=', self.building_id.id)]
        if self.floor_id:
            dom += [('floor_id', '=', self.floor_id.id)]
        if self.room_id:
            dom += [('room_id', '=', self.room_id.id)]
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
        self.results = Result.search(dom)
        where_str = self._domain_to_where_str(dom)
        self._cr.execute("""
            select a.*, id asset_id,
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
                        concat('res.section,', a.section_id)
                     when a.owner_project_id is not null then
                        concat('res.project,', a.project_id)
                     when a.owner_invest_asset_id is not null then
                        concat('res.invest.asset,', a.invest_asset_id)
                     when a.owner_invest_construction_phase_id is not null
                        then concat('res.invest.construction.phase,',
                                     a.invest_construction_phase_id)
                     else null end as owner_budget,
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
                 and ml.date <= %s -- date start
                 and asset_id = a.id) accumulated_bf
            from
            account_asset a where
        """ + where_str, (tuple(depre_account_ids), date_start, date_end,
                          tuple(accum_depre_account_ids), date_end,
                          tuple(accum_depre_account_ids), date_start))
        results = self._cr.dictfetchall()
        ReportLine = self.env['asset.register.view']
        for line in results:
            self.results += ReportLine.new(line)

    @api.multi
    def action_get_report(self):
        action = self.env.ref(
            'pabi_account_report.action_asset_register_report_form')
        action.write({'context': {'wizard_id': self.id}})
        return super(AssetRegisterReport, self).action_get_report()
