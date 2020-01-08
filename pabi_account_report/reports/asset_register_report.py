# -*- coding: utf-8 -*-
import base64
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


REFERENCE_SELECT = [
    ('res.section', 'Section'),
    ('res.project', 'Project'),
    ('res.invest.asset', 'Invest Asset'),
    ('res.invest.construction.phase', 'Invest Construction Phase'),
]


@job(default_channel='root.xlsx_asset_report')
def action_export_excel(session, model_name, res_id, report_name):
    try:
        report = session.env['ir.actions.report.xml'].search([
            ('report_name', '=', report_name),
            ('report_type', '=', 'xlsx'),
        ])
        out_file, report_type = report.render_report([res_id], report_name, {})
        out_file = base64.b64encode(out_file)
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
        out_name = report.name.replace(' ', '')
        out_name = '%s_%s' % (out_name, ts.strftime('%Y%m%d_%H%M%S'))
        session.env['ir.attachment'].create({
            'name': '%s.xlsx' % out_name,
            'datas': out_file,
            'datas_fname': '%s.xlsx' % out_name,
            'res_model': 'queue.job',
            'res_id': job.id,
            'type': 'binary',
            'parent_id': session.env.ref('pabi_utils.dir_spool_report').id,
            'description': desc,
            'user_id': job.user_id.id,
        })
        # Result Description
        result = _('Successfully created excel report : %s.xlsx') % out_name
        return result
    except Exception, e:
        raise FailedJobError(e)


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
    asset_state = fields.Many2many(
        'xlsx.report.status',
        string='Asset State',
        domain=[('location', '=', 'asset.register.view')],
        default=lambda self: self.env['xlsx.report.status'].search([
            ('location', '=', 'asset.register.view'),
            ('status', 'in', ['draft', 'open', 'close'])]),
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
    asset_active = fields.Selection(
        [('active', 'Active'),
         ('inactive', 'Inactive')],
        string='Asset Active',
        default='active',
    )
    results = fields.Many2many(
        'asset.register.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _get_filter_many2many(self, obj_ids, attribute):
        obj_name = obj_ids.mapped(attribute)
        name_filter = ', '.join(x for x in obj_name)
        return name_filter or _('')

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
            dom += [('owner_org_id', 'in', tuple(self.org_ids.ids + [0]))]
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
            res, state_name = [], self.asset_state
            for state in self.asset_state:
                state_name = self.env['xlsx.report.status'].search([
                    ('id', '=', state.id)])
                res += [str(state_name.status)]
            if len(self.asset_state) == 1:
                dom += [('state', '=', str(state_name.status))]
            else:
                dom += [('state', 'in', tuple(res))]

        if self.building_ids:
            dom += [('building_id', 'in', tuple(self.building_ids.ids + [0]))]
        if self.floor_ids:
            dom += [('floor_id', 'in', tuple(self.floor_ids.ids + [0]))]
        if self.room_ids:
            dom += [('room_id', 'in', tuple(self.room_ids.ids + [0]))]
        if self.asset_active:
            dom += [('active', '=', True if (self.asset_active == 'active')
                    else False)]
        # date_start <= date_end
        if self.date_end:
            dom += [('date_start', '<=', self.date_end)]

        # Prepare fixed params
        date_start = False
        date_end = False

        if self.filter == 'filter_date':
            date_start = self.date_start  # self.fiscalyear_start_id.date_start
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
                  CAST(%s AS int) then a.purchase_value
                 else null end as purchase_before_current,
                -- purchase_current
                case when date_part('year', a.date_start+92) =
                 CAST(%s AS int) then a.purchase_value
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
                -- owner_org_id
                case
                    when a.owner_section_id is not null then rs.org_id
                    when a.owner_project_id is not null then rp.org_id
                    when a.owner_invest_asset_id is not null then ria.org_id
                    when a.owner_invest_construction_phase_id is not null
                    then ricp.org_id else null
                end as owner_org_id,
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
                         (self.fiscalyear_start_id.name,
                          self.fiscalyear_start_id.name,
                          tuple(accum_depre_account_ids), date_end,
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

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        report_name = 'report_asset_register_xlsx'
        if self.async_process:
            Job = self.env['queue.job']
            session = ConnectorSession(self._cr, self._uid, self._context)
            description = 'Excel Report - %s' % (self._name)
            uuid = action_export_excel.delay(
                session, self._name, self.id, report_name,
                description=description)
            job = Job.search([('uuid', '=', uuid)], limit=1)
            # Process Name
            job.process_id = self.env.ref('pabi_utils.xlsx_report')
            self.write({'state': 'get', 'uuid': uuid})
            result = {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
        else:
            result = self.env['report'].get_action(self, report_name)
        return result

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
