# -*- coding: utf-8 -*-
from openerp import api, models, fields


class CostControlBreakdown(models.TransientModel):
    _inherit = "cost.control.breakdown"

    @api.model
    def _prepare_breakdown_line_dict(self, line):
        vals = super(CostControlBreakdown, self).\
            _prepare_breakdown_line_dict(line)
        vals.update({'charge_type': line.charge_type})
        return vals


class CostControlBreakdownLine(models.TransientModel):
    _inherit = "cost.control.breakdown.line"

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Internal charged is for Unit Based only."
    )
