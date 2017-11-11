# -*- coding: utf-8 -*-
from openerp import fields, models


class AccountBudget(models.Model):
    _inherit = "account.budget"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=True,
        # domain=lambda self: self.env['operating.unit']._ou_domain(),
    )


class AccountBudgetLines(models.Model):
    _inherit = "account.budget.line"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        required=False,
    )
