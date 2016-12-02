# -*- coding: utf-8 -*-
from openerp import api, models, fields


class JobOrderBreakdown(models.TransientModel):
    _inherit = "budget.job.order.breakdown"

    @api.model
    def _prepare_breakdown_line_dict(self, line):
        vals = super(JobOrderBreakdown, self).\
            _prepare_breakdown_line_dict(line)
        vals.update({'charge_type': line.charge_type})
        return vals


class JobOrderBreakdownLine(models.TransientModel):
    _inherit = "budget.unit.job.order.line"

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Internal charged is for Unit Based only."
    )
