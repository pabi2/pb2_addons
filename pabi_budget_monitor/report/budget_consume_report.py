# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import tools
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, CHART_VIEW_LIST, ChartField


class BudgetConsumeReport(ChartField, models.Model):
    _inherit = 'budget.consume.report'

    document = fields.Char(
        string='Document',
        readonly=True,
        help="Reference to original document",
    )
    # program_rpt_id = fields.Many2one(
    #     'res.program',
    #     string='Report Program',
    # )

    # def _get_sql_view(self):
    #     sql_view = super(BudgetConsumeReport, self)._get_sql_view()
    #     join_query = """
    #         left join res_section section on section.id = aal.section_id
    #         left join res_project project on project.id = aal.project_id
    #     """
    #     sql_view = sql_view + join_query
    #     return sql_view
    def _get_from_clause(self):
        sql_from = super(BudgetConsumeReport, self)._get_from_clause()
        join_sql = """
            left join res_section section on section.id = aal.section_id
            left join res_project project on project.id = aal.project_id
        """
        sql_from += join_sql
        return sql_from

    def _get_dimension(self):
        dimensions = super(BudgetConsumeReport, self)._get_dimension()
        # Add dimensions from chart field
        for d in dict(CHART_FIELDS).keys():
            dimensions += ', aal.%s' % (d,)
        dimensions += ', aal.chart_view'
        # Add dimensions for document reference
        dimensions += ', aal.document'
        # dimensions += '''
        #   , CASE WHEN aal.section_id is not null THEN section.program_rpt_id
        #          WHEN aal.project_id is not null THEN project.program_rpt_id
        #             END as program_rpt_id'''
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))


class BudgetCommitmentSummary(models.Model):
    _inherit = 'budget.commitment.summary'

    budget_name = fields.Char(
        string='Budget',
        compute='_compute_budget_name',
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
    )
    org_id = fields.Many2one(
        'res.org',
        string='Section',
        readonly=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Org',
        readonly=True,
    )
    program_id = fields.Many2one(
        'res.program',
        string='Program',
        readonly=True,
    )
    project_id = fields.Many2one(
        'res.project',
        string='Project',
        readonly=True,
    )
    invest_construction_phase_id = fields.Many2one(
        'res.invest.construction.phase',
        string='Construction Phase',
        readonly=True,
    )
    invest_asset_id = fields.Many2one(
        'res.invest.assset',
        string='Invest Asset',
        readonly=True,
    )
    personnel_costcenter_id = fields.Many2one(
        'res.personnel.costcenter',
        string='Personnel Costcenter',
        readonly=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
        readonly=True,
    )

    @api.multi
    def _compute_budget_name(self):
        for rec in self:
            rec.budget_name = rec.section_id.display_name or \
                rec.project_id.display_name or \
                rec.invest_construction_phase_id.display_name or \
                rec.invest_asset_id.display_name or \
                rec.personnel_costcenter_id.display_name or False

    def _get_dimension(self):
        dimensions = super(BudgetCommitmentSummary, self)._get_dimension()
        dimensions += """
        , chart_view, cost_control_id, org_id, program_id,
        section_id, invest_asset_id, project_id,
        invest_construction_phase_id, personnel_costcenter_id
        """
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
