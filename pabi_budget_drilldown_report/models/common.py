# -*- coding: utf-8 -*-
from openerp import api, fields
from openerp.addons.pabi_chartfield.models.chartfield import \
    ChartField, CHART_VIEW_LIST


REPORT_TYPES = [('overall', 'Overall'),
                ('unit_base', 'Section'),
                ('project_base', 'Project'),
                ('invest_asset', 'Asset'),
                ('invest_construction', 'Construction'),
                ('personnel', 'Personnel')]


class SearchCommon(ChartField, object):
    """ This class add some common search options """

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
        readonly=True,
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        readonly=True,
    )
    report_type = fields.Selection(
        REPORT_TYPES,
        string='Report Type',
        required=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    # ------------ SEARCH ------------
    # For: All report types
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
    division_id = fields.Many2one(
        'res.division',
        string='Division',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )

    @api.onchange('org_id')
    def _onchange_org_id(self):
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('sector_id')
    def _onchange_sector_id(self):
        self.org_id = False
        self.subsector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('subsector_id')
    def _onchange_subsector_id(self):
        self.org_id = False
        self.sector_id = False
        self.division_id = False
        self.section_id = False

    @api.onchange('division_id')
    def _onchange_division_id(self):
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.section_id = False

    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.org_id = False
        self.sector_id = False
        self.subsector_id = False
        self.division_id = False
