# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    in_unit_transfer_ids = fields.One2many(
        'section.budget.transfer.line',
        'to_budget_id',
        string='Transfer In',
        readonly=True,
        copy=False,
    )
    out_unit_transfer_ids = fields.One2many(
        'section.budget.transfer.line',
        'from_budget_id',
        string='Transfer In',
        readonly=True,
        copy=False,
    )
