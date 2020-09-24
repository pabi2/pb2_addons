# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class AccountBudget(models.Model):
    _inherit = "account.budget"

    budget_init_line_ids = fields.One2many(
        'account.budget.init.line',
        'budget_id',
        string='Budget Lines',
        readonly=True,
        copy=False,
    )
    budgeted_expense_init = fields.Float()
    policy_amount_init = fields.Float()
    released_amount_init = fields.Float()
    budgeted_expense_init_internal = fields.Float()
    budgeted_expense_init_external = fields.Float()

    @api.multi
    def _prepare_init_budget_line(self, lines):
        self.ensure_one()
        data_dict = [(0, 0, {
            'budget_id': line.budget_id.id,
            'charge_type': line.charge_type,
            'income_section_id': line.income_section_id.id,
            'fund_id': line.fund_id.id,
            'cost_control_id': line.cost_control_id.id,
            'activity_group_id': line.activity_group_id.id,
            'description': line.description,
            'planned_amount': line.planned_amount,
            'released_amount': line.released_amount,
            'm1': line.m1,
            'm2': line.m2,
            'm3': line.m3,
            'm4': line.m4,
            'm5': line.m5,
            'm6': line.m6,
            'm7': line.m7,
            'm8': line.m8,
            'm9': line.m9,
            'm10': line.m10,
            'm11': line.m11,
            'm12': line.m12,
        }) for line in lines]
        return data_dict

    @api.multi
    def action_init(self):
        if self.filtered(lambda l: not l.budget_expense_line_unit_base):
            raise ValidationError(_('Expense line(s) is empty.'))
        # create init line 1 time only
        if self.filtered(lambda l: l.budget_init_line_ids):
            raise ValidationError(_(
                'You can created Expense line init 1 time only.'))
        for rec in self:
            data_dict = rec._prepare_init_budget_line(
                rec.budget_expense_line_unit_base)
            amounts = rec.budget_expense_line_ids.mapped('planned_amount')
            rec.write({
                'budgeted_expense_init_internal':
                rec.budgeted_expense_internal,
                'budgeted_expense_init_external':
                rec.budgeted_expense_external,
                'budgeted_expense_init': sum(amounts),
                'policy_amount_init': rec.policy_amount or 0.0,
                'released_amount_init': rec.released_amount or 0.0,
                'budget_init_line_ids': data_dict
            })
        return True

    @api.multi
    def action_open_budget_init(self):
        self.ensure_one()
        action = \
            self.env.ref('account_budget_control_init.action_budget_init_view')
        result = action.read()[0]
        result.update({'res_id': self.id})
        return result
