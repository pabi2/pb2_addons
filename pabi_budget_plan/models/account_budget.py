# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountBudget(models.Model):
    _inherit = 'account.budget'

    prev_planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
        readonly=False,  # TODO: change back to True
    )
    planned_amount = fields.Float(
        string='Current Amount',  # Existing field, change label only
        help="Current Planned Amount",
    )

    @api.multi
    def budget_confirm(self):
        for rec in self:
            if rec.planned_amount != rec.policy_amount:
                raise UserError(_('New amount must equal to Policy Amount'))
        return super(AccountBudget, self).budget_confirm()


class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    planned_amount = fields.Float(
        string='Current Amount',  # Existing field, change label only
        help="Current Planned Amount"
    )
