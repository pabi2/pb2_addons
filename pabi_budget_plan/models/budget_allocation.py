# -*- coding: utf-8 -*-
import time
from openerp.tools import float_compare
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, ChartField


class BudgetAllocation(models.Model):
    _name = 'budget.allocation'
    _inherit = ['mail.thread']
    _description = 'Budget Allocation'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        index=True,
        ondelete='cascade',
    )
    revision = fields.Selection(
        lambda self: [(str(x), str(x))for x in range(13)],
        string='Revision',
        readonly=True,
        help="Revision 0 - 12, 0 is on on the fiscalyear open.",
    )
    amount_unit_base = fields.Float(
        string='Unit Based',
    )
    amount_project_base = fields.Float(
        string='Project Based',
    )
    amount_personnel = fields.Float(
        string='Personnel Budget',
    )
    amount_invest_asset = fields.Float(
        string='Invest Asset',
    )
    amount_invest_construction = fields.Float(
        string='Invest Construction',
    )
    _sql_constraints = [
        ('uniq_revision', 'unique(fiscalyear_id, revision)',
         'Duplicated revision of budget policy is not allowed!'),
    ]
