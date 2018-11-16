# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField
from openerp.addons.pabi_account_move_document_ref.models.account_move import \
    DOCTYPE_SELECT


class BudgetMonitorReport(ChartField, models.Model):
    _inherit = 'budget.monitor.report'

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

    def _get_dimension(self):
        # Add dimensions from chart field
        dimensions = super(BudgetMonitorReport, self)._get_dimension()
        for d in dict(CHART_FIELDS).keys():
            dimensions += ', %s' % (d,)
        dimensions += ', chart_view'
        # Add document reference
        dimensions += ', doctype, document, document_line'
        # dimensions += ', program_rpt_id'
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
