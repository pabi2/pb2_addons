# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetConsumeReport(models.Model):
    _inherit = 'budget.consume.report'
    _auto = False

    activity_rpt_id = fields.Many2one(
        'account.activity',
        string='Activity Rpt',
    )

    def _get_dimension(self):
        dimensions = super(BudgetConsumeReport, self)._get_dimension()
        return dimensions + ', activity_rpt_id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
