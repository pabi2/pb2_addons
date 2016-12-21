# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_FIELDS, ChartField


class BudgetConsumeReport(ChartField, models.Model):
    _inherit = 'budget.consume.report'

    document = fields.Char(
        string='Document',
        readonly=True,
        help="Reference to original document",
    )

    def _get_dimension(self):
        dimensions = super(BudgetConsumeReport, self)._get_dimension()
        # Add dimensions from chart field
        for d in dict(CHART_FIELDS).keys():
            dimensions += ', aal.%s' % (d,)
        dimensions += ', aal.chart_view'
        # Add dimensions for document reference
        dimensions += ', aal.document'
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
