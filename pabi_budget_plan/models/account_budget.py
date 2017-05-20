# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning as UserError


class AccountBudget(models.Model):
    _inherit = 'account.budget'
    _order = 'create_date desc'

    @api.model
    def _get_currency(self):
        company = self.env.user.company_id
        currency = company.currency_id
        return currency

    prev_planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
        readonly=False,  # TODO: change back to True
    )
    ref_budget_id = fields.Many2one(
        'account.budget',
        string="Previous Budget",
        copy=False,
        readonly=True,
    )
    ref_breakdown_id = fields.Many2one(
        'budget.fiscal.policy.breakdown',
        string="Breakdown Reference",
        copy=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=_get_currency,
        readonly=True,
    )
    company_id = fields.Many2one(
        readonly=True,
    )

    @api.model
    def create(self, vals):
        budget = super(AccountBudget, self).create(vals)
        budget_level = budget.budget_level_id
        if budget_level.budget_release == 'manual_header' and \
                budget_level.release_follow_policy and \
                'policy_amount' in vals:
            vals['to_release_amount'] = vals['policy_amount']
            budget.write(vals)
        return budget

    @api.multi
    def write(self, vals):
        if 'policy_amount' in vals:
            for budget in self:
                budget_level = budget.budget_level_id
                if budget_level.budget_release == 'manual_header' and \
                        budget_level.release_follow_policy:
                    vals['to_release_amount'] = vals['policy_amount']
                super(AccountBudget, budget).write(vals)
        else:
            super(AccountBudget, self).write(vals)
        return True

    @api.one
    @api.constrains('fiscalyear_id', 'section_id')
    def _check_fiscalyear_section_unique(self):
        if self.fiscalyear_id and self.section_id:
            budget = self.search(
                [('version', '=', self.version),
                 ('fiscalyear_id', '=', self.fiscalyear_id.id),
                 ('section_id', '=', self.section_id.id),
                 ('state', '!=', 'cancel'), ])
            if len(budget) > 1:
                raise ValidationError(
                    _('You can not have duplicate budget control for '
                      'same fiscalyear, section and version.'))

    @api.multi
    def _validate_plan_amount(self):
        self.ensure_one()
        if self.budget_level_id.check_plan_with_released_amount:
            if self.rolling > self.released_amount:
                raise UserError(
                    _('New rolling plan must not exceed released amount'))
        return True

    @api.multi
    def budget_confirm(self):
        for rec in self:
            rec._validate_plan_amount()
            name = self.env['ir.sequence'].next_by_code('budget.control.unit')
            rec.write({'name': name})
            rec.ref_budget_id.budget_cancel()
        return super(AccountBudget, self).budget_confirm()

    # New Revision
    @api.multi
    def new_minor_revision(self):
        result = super(AccountBudget, self).new_minor_revision()
        if result.get('domain', []):
            new_budget_id = result['domain'][0][2]
            new_budget = self.browse(new_budget_id)
            new_budget.ref_budget_id = self.id
            new_budget.name = '/'
        return result

    @api.multi
    def unlink(self):
        for policy in self:
            if policy.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('Cannot delete budget(s)\
                    which are not in draft or cancelled.'))
        return super(AccountBudget, self).unlink()

    @api.multi
    def get_all_version(self):
        self.ensure_one()
        budget_ids = []
        if self.ref_budget_id:
            budget = self.ref_budget_id
            while budget:
                budget_ids.append(budget.id)
                budget = budget.ref_budget_id
        budget = self
        while budget:
            ref_budget =\
                self.search([('ref_budget_id', '=', budget.id)])
            if ref_budget:
                budget_ids.append(ref_budget.id)
            budget = ref_budget
        act = 'account_budget_activity.act_account_budget_view'
        action = self.env.ref(act)
        result = action.read()[0]
        dom = [('id', 'in', budget_ids)]
        result.update({'domain': dom})
        return result


class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    planned_amount = fields.Float(
        string='Current Amount',  # Existing field, change label only
        help="Current Planned Amount"
    )
