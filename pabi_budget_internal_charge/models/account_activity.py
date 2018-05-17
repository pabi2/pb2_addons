# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountActivity(models.Model):
    _inherit = "account.activity"

    internal_charge = fields.Boolean(
        string='Internal Charge',
        default=False,
        help="For external internal charge, it will refer "
        "to income side internal charge",
    )
    inrev_activity_ids = fields.Many2many(
        'account.activity',
        'activity_inrev_activity_rel',
        'inexp_activity_id', 'inrev_activity_id',
        string='Internal Revenue Activity',
        domain=[('budget_method', '=', 'revenue')],
    )
    inexp_activity_ids = fields.Many2many(
        'account.activity',
        'activity_inrev_activity_rel',
        'inrev_activity_id', 'inexp_activity_id',
        string='Internal Expense Activity',
        help="The inverse of inrev_activity_ids",
        domain=[('budget_method', '=', 'expense')],
    )

    @api.onchange('internal_charge')
    def _onchange_internal_charge(self):
        self.inrev_activity_ids = False
