# -*- coding: utf-8 -*-
from openerp import models, fields


class BudgetPlanLineTemplate(models.Model):
    _inherit = "budget.plan.line.template"

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Internal charged is for Unit Based only."
    )
