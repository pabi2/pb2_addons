# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField
from openerp.addons.pabi_account_move_document_ref.models.account_move import \
    DOCTYPE_SELECT


class BudgetPlanReport(ChartField, models.Model):
    _inherit = 'budget.plan.report'

    doctype = fields.Selection(
        DOCTYPE_SELECT,
        string='Doctype',
        readonly=True,
    )
    document = fields.Char(
        string='Document',
        readonly=True,
        help="Reference to original document",
    )
    document_line = fields.Char(
        string='Document Line',
        readonly=True,
        help="Reference to original document line",
    )
    # program_rpt_id = fields.Many2one(
    #     'res.program',
    #     string='Report Program',
    # )

    def _get_sql_view(self):
        sql_view = super(BudgetPlanReport, self)._get_sql_view()
        join_query = """
            left join res_section section on section.id = abl.section_id
            left join res_project project on project.id = abl.project_id
        """
        sql_view = sql_view + join_query
        return sql_view

    def _get_dimension(self):
        # Add dimensions from chart field
        dimensions = super(BudgetPlanReport, self)._get_dimension()
        for d in dict(CHART_FIELDS).keys():
            dimensions += ', abl.%s' % (d,)
        dimensions += ', abl.chart_view'
        # Add document reference
        dimensions += """, 'account_budget' as doctype,
        ab.name as document, abl.description as document_line"""
    # dimensions += """
    #     , CASE WHEN abl.section_id is not null THEN section.program_rpt_id
    #            WHEN abl.project_id is not null THEN project.program_rpt_id
    #       END as program_rpt_id"""
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
