# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the budget plan line is for Internal Charge or "
        "External Charge. Only expense internal charge to be set as internal",
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        required=True,
        default='external',
        help="Specify whether the move line is for Internal Charge or "
        "External Charge. Only expense internal charge to be set as internal",
    )

    @api.model
    def _prepare_analytic_line(self, obj_line):
        vals = super(AccountMoveLine, self)._prepare_analytic_line(obj_line)
        if obj_line.charge_type == 'internal':
            vals['charge_type'] = 'internal'
        return vals
