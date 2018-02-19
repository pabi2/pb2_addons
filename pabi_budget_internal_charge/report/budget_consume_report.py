# -*- coding: utf-8 -*-
from openerp import models, fields
from openerp import tools


class BudgetConsumeReport(models.Model):
    _inherit = 'budget.consume.report'

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )

    def _get_dimension(self):
        dimensions = super(BudgetConsumeReport, self)._get_dimension()
        dimensions += ', aal.charge_type'
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))


class BudgetCommitmentSummary(models.Model):
    _inherit = 'budget.commitment.summary'

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
        readonly=True,
    )

    def _get_dimension(self):
        dimensions = super(BudgetCommitmentSummary, self)._get_dimension()
        dimensions += ', charge_type, cost_control_id, section_id'
        return dimensions

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
