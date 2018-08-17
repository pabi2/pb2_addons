# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    policy_amount = fields.Float(
        readony=False,
        help="Editable only in pabi__pre_go_live",
    )
