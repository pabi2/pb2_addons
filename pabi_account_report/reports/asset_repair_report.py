# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools

REFERENCE_SELECT = [
    ('res.section', 'Section'),
    ('res.project', 'Project'),
    ('res.invest.asset', 'Invest Asset'),
    ('res.invest.construction.phase', 'Invest Construction Phase'),
]


class AssetRepairView(models.Model):
    _name = 'asset.repair.view'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Account Asset Id',
        readonly=True,
    )
    asset_repair_id = fields.Many2one(
        'asset.repair.note',
        string='Asset Repair Id',
        readonly=True,
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order Id',
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter Id',
        readonly=True,
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        readonly=True,
    )
    budget = fields.Reference(
        REFERENCE_SELECT,
        string='Budget',
        readonly=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section id',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """
            SELECT ROW_NUMBER() OVER(ORDER BY acr.id, ac.id) AS id,
                ac.id as asset_id, acr.id as asset_repair_id,
                po.id as purchase_order_id, rc.id as costcenter_id,
                ac.responsible_user_id, ac.section_id,
                CASE WHEN ac.section_id IS NOT NULL THEN
                CONCAT('res.section,', ac.section_id)
                WHEN ac.project_id IS NOT NULL THEN
                CONCAT('res.project,', ac.project_id)
                WHEN ac.invest_asset_id IS NOT NULL THEN
                CONCAT('res.invest.asset,', ac.invest_asset_id)
                WHEN ac.invest_construction_phase_id IS NOT NULL THEN
                CONCAT('res.invest.construction.phase,',
                ac.invest_construction_phase_id)
                ELSE NULL END AS budget
                FROM asset_repair_note acr
                JOIN account_asset ac ON acr.asset_id = ac.id
                JOIN res_costcenter rc ON ac.costcenter_id = rc.id
                LEFT JOIN purchase_order po ON acr.purchase_id = po.id
        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportAssetRepair(models.TransientModel):
    _name = 'xlsx.report.asset.repair'
    _inherit = 'report.account.common'

    org_id = fields.Many2one(
        'res.org',
        string='Orgs',
    )
    sector_id = fields.Many2one(
        'res.sector',
        string='Sector',
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Asset',
    )
    responsible_by = fields.Many2one(
        'res.users',
        string='Responsible Person',
    )
    status_id = fields.Many2one(
        'account.asset.status',
        string='Status',
    )
    budget = fields.Many2one(
        'chartfield.view',
        string='Source of Budget',
    )
    as_of_date = fields.Date(
        string='As of Date',
        required=True,
    )
    results = fields.Many2many(
        'asset.repair.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['asset.repair.view']
        dom = []
        if self.org_id:
            dom += [('asset_repair_id.asset_id.org_id',
                     '=', self.org_id.ids)]
        if self.sector_id:
            dom += [('asset_repair_id.asset_id.sector_id',
                     '=', self.sector_id.ids)]
        if self.subsector_id:
            dom += [('asset_repair_id.asset_id.subsector_id',
                     '=', self.subsector_id.ids)]
        if self.division_id:
            dom += [('asset_repair_id.asset_id.division_id',
                     '=', self.division_id.ids)]
        if self.section_id:
            dom += [('section_id', '=', self.section_id.ids)]
        if self.asset_id:
            dom += [('asset_repair_id.asset_id.id',
                     '=', self.asset_id.ids)]
        if self.responsible_by:
            dom += [('asset_repair_id.asset_id.responsible_user_id',
                    '=', self.responsible_by.ids)]
        if self.status_id:
            dom += [('asset_repair_id.asset_id.status',
                     '=', self.status_id.ids)]
        if self.as_of_date:
            dom += [('asset_repair_id.date', '<=', self.as_of_date)]
        if self.budget:
            dom_budget = str(self.budget.model) + ',' + str(self.budget.res_id)
            dom += [('budget', '=', dom_budget)]

        self.results = Result.search(dom)

    @api.onchange('org_id')
    def _onchange_org_id(self):
        if self.org_id:
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False
            self.responsible_by = False

    @api.onchange('sector_id')
    def _onchange_sector_id(self):
        if self.sector_id:
            self.org_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False
            self.responsible_by = False

    @api.onchange('subsector_id')
    def _onchange_subsector_id(self):
        if self.subsector_id:
            self.org_id = False
            self.sector_id = False
            self.division_id = False
            self.section_id = False
            self.responsible_by = False

    @api.onchange('division_id')
    def _onchange_division_id(self):
        if self.division_id:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.section_id = False
            self.responsible_by = False

    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False
            self.responsible_by = False

    @api.onchange('responsible_by')
    def _onchange_responsible_by(self):
        if self.responsible_by:
            self.org_id = False
            self.sector_id = False
            self.subsector_id = False
            self.division_id = False
            self.section_id = False
