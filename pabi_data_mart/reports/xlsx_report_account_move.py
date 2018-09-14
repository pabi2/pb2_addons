# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
import time


class AccountMoveDataMartView(models.Model):
    _name = 'account.move.data.mart.view'
    _description = 'Account Move Data Mart'
    _auto = False

    move_id = fields.Integer(
        string='Account move',
        readonly=True,
    )
    auto_reconcile_id = fields.Many2one(
        'account.auto.reconcile',
        string='Auto Reconcile',
        readonly=True,
    )
    cancel_entry = fields.Char(
        string='Cancel Entry',
        readonly=True,
    )
    date_document = fields.Date(
        string='Date Document',
        readonly=True,
    )
    date_value = fields.Date(
        string='Date Value',
        readonly=True,
    )
    doctype = fields.Char(
        string='Doctype',
        readonly=True,
    )
    document = fields.Char(
        string='Document',
        readonly=True,
    )
    document_id = fields.Char(
        string='Document ID',
        readonly=True,
    )
    line_item_summary = fields.Char(
        string='Line Item Summary',
        readonly=True,
    )
    model_id = fields.Many2one(
        'account.model',
        string='Account Model',
        readonly=True,
    )
    narration = fields.Char(
        string='Narration',
        readonly=True,
    )
    ref = fields.Char(
        string='Ref',
        readonly=True,
    )
    reversal_id = fields.Char(
        string='Reversal ID',
        readonly=True,
    )
    move_state = fields.Char(
        string='Move State',
        readonly=True,
    )
    system_id = fields.Many2one(
        'interface.system',
        string='interface System',
        readonly=True,
    )
    to_be_reversed = fields.Char(
        string='To Be Reversed',
        readonly=True,
    )
    to_check = fields.Char(
        string='To Check',
        readonly=True,
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string='Account Move Line',
        readonly=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        readonly=True,
    )
    account_tax_id = fields.Many2one(
        'account.tax',
        string='Account Tax',
        readonly=True,
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Account Activity Group',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Account Activity',
        readonly=True,
    )
    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Account Activity rpt',
        readonly=True,
    )
    amount_currency = fields.Integer(
        string='Amount Currency',
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        readonly=True,
    )
    asset_id = fields.Many2one(
        'account.asset',
        string='Account Asset',
        readonly=True,
    )
    asset_profile_id = fields.Many2one(
        'account.asset.profile',
        string='Account Asset Profile',
        readonly=True,
    )
    bank_receipt_id = fields.Integer(
        string='Bank Receipt ID',
        readonly=True,
    )
    blocked = fields.Char(
        string='Blocked',
        readonly=True,
    )
    centralisation = fields.Char(
        string='Centralisation',
        readonly=True,
    )
    charge_type = fields.Char(
        string='Charge Type',
        readonly=True,
    )
    chart_view = fields.Char(
        string='Charge View',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        readonly=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Cost Control',
        readonly=True,
    )
    cost_control_type_id = fields.Many2one(
        'cost.control.type',
        string='Cost Control Type',
        readonly=True,
    )
    create_date = fields.Date(
        string='Creat Date',
        readonly=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        string='Users',
        readonly=True,
    )
    credit = fields.Integer(
        string='Credit',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
    )
    date = fields.Date(
        string='Date',
        readonly=True,
    )
    date_created = fields.Date(
        string='Date Created',
        readonly=True,
    )
    date_maturity = fields.Date(
        string='Date Maturity',
        readonly=True,
    )
    date_reconciled = fields.Date(
        string='Date Reconciled',
        readonly=True,
    )
    debit = fields.Integer(
        string='Debit',
        readonly=True,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        readonly=True,
    )
    docline_seq = fields.Integer(
        string='Docline Seq',
        readonly=True,
    )
    functional_area_id = fields.Many2one(
        'res.functional.area',
        string='Functional Area',
        readonly=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        readonly=True,
    )
    invest_asset_id = fields.Many2one(
        'res.invest.asset',
        string='Invest Asset',
        readonly=True,
    )
    invest_construction_id = fields.Many2one(
        'res.invest.construction',
        string='Invest Construction',
        readonly=True,
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Invest Construction Phase',
        readonly=True,
    )
    investment_id = fields.Integer(
        string='Investment ID',
        readonly=True,
    )
    is_tax_line = fields.Char(
        string='Is Tax Line',
        readonly=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='account journal',
        readonly=True,
    )
    last_rec_date = fields.Date(
        string='Last Rec Date',
        readonly=True,
    )
    match_import_id = fields.Integer(
        string='Match Import ID',
        readonly=True,
    )
    mission_id = fields.Many2one(
        'res.mission',
        string='Mission',
        readonly=True,
    )
    name = fields.Char(
        string='Name',
        readonly=True,
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        readonly=True,
    )
    parent_asset_id = fields.Many2one(
        'account.asset',
        string='Parent Asset ',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner Code',
        readonly=True,
    )
    period_id = fields.Many2one(
        'account.period',
        string='Account Period',
        readonly=True,
    )
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Budget Code ',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        readonly=True,
    )
    product_uom_id = fields.Many2one(
         'product.uom',
         string='Product uom',
         readonly=True,
    )
    program_group_id = fields.Many2one(
         'res.program.group',
         string='Program Group',
         readonly=True,
    )
    program_id = fields.Many2one(
          'res.program',
          string='Program',
          readonly=True,
    )
    project_group_id = fields.Many2one(
          'res.project.group',
          string='Project Group Code',
          readonly=True,
    )
    project_id = fields.Many2one(
          'res.project',
          string='Project',
          readonly=True,
    )
    quantity = fields.Integer(
        string='Quantity',
        readonly=True,
    )
    reconcile_id = fields.Many2one(
          'account.move.reconcile',
          string='Reconcile',
          readonly=True,
    )
    reconcile_partial_id = fields.Many2one(
          'account.move.reconcile',
          string='Partial Reconcile',
          readonly=True,
    )
    reconcile_ref = fields.Char(
        string='Reconcile Ref.',
        readonly=True,
    )
    section_id = fields.Many2one(
          'res.section',
          string='Section',
          readonly=True,
    )
    section_program_id = fields.Many2one(
          'res.section.program',
          string='Section Program',
          readonly=True,
    )
    sector_id = fields.Many2one(
          'res.sector',
          string='Sector',
          readonly=True,
    )
    spa_id = fields.Many2one(
          'res.spa',
          string='SPA',
          readonly=True,
    )
    state = fields.Char(
        string='State',
        readonly=True,
    )
    statement_id = fields.Integer(
        string='Statement',
        readonly=True,
    )
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True,
    )
    subsector_id = fields.Many2one(
        'res.subsector',
        string='Subsector',
        readonly=True,
    )
    tag_id = fields.Many2one(
        'res.tag',
        string='Tag',
        readonly=True,
    )
    tag_type_id = fields.Many2one(
        'res.tag.type',
        string='Tag Type',
        readonly=True,
    )
    tax_amount = fields.Integer(
        string='Tax Amount',
        readonly=True,
    )
    taxbranch_id = fields.Many2one(
        'res.taxbranch',
        string='Tax Branch',
        readonly=True,
    )
    tax_code_id = fields.Many2one(
        'account.tax.code',
        string='Tax Code',
        readonly=True,
    )
    write_date = fields.Date(
        string='Write Date',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        string='Users',
        readonly=True,
    )

    def _get_sql_view(self):
        sql_view = """

            SELECT l.id,
            m.id as move_id, m.auto_reconcile_id, m.cancel_entry,
            m.date_document, m.date_value, m.doctype, m.document,m.document_id,
            m.line_item_summary, m.model_id, m.narration, m.ref, m.reversal_id,
            m.state AS move_state, m.system_id, m.to_be_reversed, m.to_check,
            l.id as move_line_id, l.account_id, l.account_tax_id,
            l.activity_group_id, l.activity_id, l.activity_rpt_id,
            l.amount_currency, l.analytic_account_id, l.asset_id,
            l.asset_profile_id, l.bank_receipt_id, l.blocked, l.centralisation,
            l.charge_type, l.chart_view, l.company_id, l.costcenter_id,
            l.cost_control_id, l.cost_control_type_id, l.create_date,
            l.create_uid, l.credit, l.currency_id, l.date, l.date_created,
            l.date_maturity, l.date_reconciled, l.debit, l.division_id,
            l.docline_seq, l.functional_area_id, l.fund_id, l.invest_asset_id,
            l.invest_construction_id, l.invest_construction_phase_id,
            l.investment_id, l.is_tax_line, l.journal_id, l.last_rec_date,
            l.match_import_id, l.mission_id, l.name, l.operating_unit_id,
            l.org_id, l.parent_asset_id, l.partner_id, l.period_id,
            l.personnel_costcenter_id, l.product_id, l.product_uom_id,
            l.program_group_id, l.program_id, l.project_group_id, l.project_id,
            l.quantity, l.reconcile_id, l.reconcile_partial_id, l.reconcile_ref,
            l.section_id, l.section_program_id, l.sector_id, l.spa_id,
            l.state, l.statement_id, l.stock_move_id, l.subsector_id,
            l.tag_id, l.tag_type_id, l.tax_amount, l.taxbranch_id,l.tax_code_id,
            l.write_date, l.write_uid
            FROM account_move m
            JOIN account_move_line l ON m.id = l.move_id

        """
        return sql_view

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)"""
                   % (self._table, self._get_sql_view()))


class XLSXReportAccountMove(models.TransientModel):
    _name = 'xlsx.report.account.move'
    _inherit = 'xlsx.report'

    account_ids = fields.Many2many(
        'account.account',
        'report_id', 'account_id',
        string='Accounts',
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
    )
    chart_account_id = fields.Many2one(
        'account.account',
        string='Chart of Accounts',
        domain=[('parent_id', '=', False)],
        required=True,
        default=lambda self: self._get_account(),
        help='Select Chart of Accounts',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    fiscalyear_start_id = fields.Many2one(
        'account.fiscalyear',
        string='Start Fiscal Year',
        default=lambda self: self._get_fiscalyear(),
    )
    fiscalyear_end_id = fields.Many2one(
        'account.fiscalyear',
        string='End Fiscal Year',
        default=lambda self: self._get_fiscalyear(),
    )
    fiscalyear_date_start = fields.Date(
        string='Start Fiscal Year Date',
        compute='_compute_fiscalyear_date',
    )
    fiscalyear_date_end = fields.Date(
        string='End Fiscal Year Date',
        compute='_compute_fiscalyear_date',
    )
    filter = fields.Selection(
        [('filter_no', 'No Filters'),
         ('filter_date', 'Dates'),
         ('filter_period', 'Periods')],
        string='Filter by',
        required=True,
        default='filter_no',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    period_start_id = fields.Many2one(
        'account.period',
        string='Start Period',
    )
    period_end_id = fields.Many2one(
        'account.period',
        string='End Period',
    )
    results = fields.Many2many(
        'account.move.data.mart.view',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.model
    def _get_account(self):
        company_id = self.env.user.company_id.id
        domain = [('company_id', '=', company_id), ('parent_id', '=', False)]
        account = self.env['account.account'].search(domain, limit=1)
        return account

    @api.model
    def _get_fiscalyear(self):
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', self.env.user.company_id.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        return fiscalyear

    @api.multi
    @api.depends('fiscalyear_start_id', 'fiscalyear_end_id')
    def _compute_fiscalyear_date(self):
        self.ensure_one()
        Fiscalyear = self.env['account.fiscalyear']
        date_start = self.fiscalyear_start_id.date_start
        date_end = self.fiscalyear_end_id.date_stop
        if date_start or date_end:
            if not date_start:
                fiscalyear = Fiscalyear.search(
                    [('company_id', '=', self.company_id.id)],
                    order="date_start", limit=1)
                date_start = fiscalyear.date_start
            if not date_end:
                fiscalyear = Fiscalyear.search(
                    [('company_id', '=', self.company_id.id)],
                    order="date_stop desc", limit=1)
                date_end = fiscalyear.date_stop
        self.fiscalyear_date_start = date_start
        self.fiscalyear_date_end = date_end

    @api.multi
    def _reset_common_field(self):
        self.ensure_one()
        if not self._context.get('reset_common_field', False):
            return False
        self.fiscalyear_start_id = False
        self.fiscalyear_end_id = False
        self.period_start_id = False
        self.period_end_id = False
        self.date_start = False
        self.date_end = False
        return True

    @api.onchange('chart_account_id')
    def _onchange_chart_account_id(self):
        # Reset common field
        if self._reset_common_field():
            return {}
        # --
        company = self.chart_account_id.company_id
        now = time.strftime('%Y-%m-%d')
        domain = [('company_id', '=', company.id),
                  ('date_start', '<=', now),
                  ('date_stop', '>=', now)]
        fiscalyear = self.env['account.fiscalyear'].search(domain, limit=1)
        self.company_id = company
        self.fiscalyear_start_id = fiscalyear
        self.fiscalyear_end_id = fiscalyear
        if self.filter == "filter_period":
            Period = self.env['account.period']
            period_start = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 ('special', '=', False)], order="date_start", limit=1)
            period_end = Period.search(
                [('company_id', '=', company.id),
                 ('fiscalyear_id', '=', fiscalyear.id),
                 ('date_start', '<=', now), ('date_stop', '>=', now),
                 ('special', '=', False)], limit=1)
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = fiscalyear.date_start
            self.date_end = fiscalyear and now or False

    @api.multi
    def _get_common_period_and_date(self):
        self.ensure_one()
        period_start = period_end = False
        date_start = date_end = False
        now = time.strftime('%Y-%m-%d')
        fiscalyear_date_start = self.fiscalyear_date_start
        fiscalyear_date_end = self.fiscalyear_date_end
        Period = self.env['account.period'].with_context(
            company_id=self.company_id.id)
        if fiscalyear_date_start and fiscalyear_date_end and \
           fiscalyear_date_end >= fiscalyear_date_start:
            if now >= fiscalyear_date_start and now <= fiscalyear_date_end:
                period_start = Period.find(dt=fiscalyear_date_start)[0]
                period_end = Period.find(dt=now)[0]
                date_start = fiscalyear_date_start
                date_end = now
            elif fiscalyear_date_end < now:
                period_start = Period.find(dt=fiscalyear_date_start)[0]
                period_end = Period.find(dt=fiscalyear_date_end)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_end
            elif fiscalyear_date_start > now:
                period_start = Period.find(dt=fiscalyear_date_start)[0]
                period_end = Period.find(dt=fiscalyear_date_start)[0]
                date_start = fiscalyear_date_start
                date_end = fiscalyear_date_start
        return period_start, period_end, date_start, date_end

    @api.onchange('fiscalyear_start_id', 'fiscalyear_end_id')
    def _onchange_fiscalyear_id(self):
        period_start, period_end, date_start, date_end = \
            self._get_common_period_and_date()
        if self.filter == "filter_period":
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = date_start
            self.date_end = date_end

    @api.onchange('filter')
    def _onchange_filter(self):
        # Reset common field
        if self._reset_common_field():
            return {}
        # --
        period_start, period_end, date_start, date_end = \
            self._get_common_period_and_date()
        self.period_start_id = self.period_end_id = False
        self.date_start = self.date_end = False
        if self.filter == "filter_period":
            self.period_start_id = period_start
            self.period_end_id = period_end
        elif self.filter == "filter_date":
            self.date_start = date_start
            self.date_end = date_end

    @api.multi
    def _compute_results(self):
        self.ensure_one()
        Result = self.env['account.move.data.mart.view']
        dom = []
        if self.account_ids:
            dom += [('account_id', 'in', self.account_ids.ids)]
        if self.partner_ids:
            dom += [('partner_id', 'in', self.partner_ids.ids)]
        if self.fiscalyear_start_id:
            dom += [('date', '>=', self.fiscalyear_start_id.date_start)]
        if self.fiscalyear_end_id:
            dom += [('date', '<=', self.fiscalyear_end_id.date_stop)]
        if self.period_start_id:
            dom += [('date', '>=', self.period_start_id.date_start)]
        if self.period_end_id:
            dom += [('date', '<=', self.period_end_id.date_stop)]
        if self.date_start:
            dom += [('date', '>=', self.date_start)]
        if self.date_end:
            dom += [('date', '<=', self.date_end)]
        self.results = Result.search(dom, order="move_id, docline_seq")
