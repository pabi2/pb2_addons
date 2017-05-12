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

    @api.model
    def _check_amount_with_policy(self):
        if self.budgeted_expense != self.policy_amount:
            raise UserError(
                _('New Budgeted Expense must equal to Policy Amount'))
        return True

    @api.multi
    def budget_confirm(self):
        for rec in self:
            rec._check_amount_with_policy()
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

    @api.multi
    def sync_budget_invest_construction(self):
        """ This method pull the invest construction phase's paln and update
        this budget's line. It will update all m1-m12 as they were approved.
        After synced, the synced = True, and it won't be pulled again.
        When phase is updated, it will reset synced = False, and ready for sync
        """
        self.ensure_one()  # Make sure it is synced one by one
        if self.chart_view != 'invest_construction':
            raise UserError(_('Not an invest construction budget control'))
        # Find matched phases for this budget control
        Phase = self.env['res.invest.construction.phase']
        PhaseSync = self.env['res.invest.construction.phase.sync']
        BudgetLine = self.env['account.budget.line']
        phases = Phase.search([
            ('org_id', '=', self.org_id.id),
            ('fiscalyear_ids', 'in', self.fiscalyear_id.id),
            ('state', '=', 'approve'),
        ])
        fiscalyear_id = self.fiscalyear_id.id
        for phase in phases:
            # Create phase sync if not exists
            phase_sync = phase.sync_ids.filtered(
                lambda l: l.fiscalyear_id.id == fiscalyear_id)
            if not phase_sync:
                phase_sync = PhaseSync.create({
                    'phase_id': phase.id,
                    'fiscalyear_id': fiscalyear_id,
                    'last_sync': False,
                    'synced': False,
                })
            # Create budget control line if not exists
            if not phase_sync.sync_budget_line_id:
                budget_line = BudgetLine.search([
                    ('budget_id', '=', self.id),
                    ('invest_construction_phase_id', '=', phase.id),
                ])
                if budget_line:
                    phase_sync.sync_budget_line_id = budget_line[0]
                else:
                    ic = phase.invest_construction_id
                    budget_line_dict = {
                        'budget_id': self.id,
                        'org_id': self.org_id.id,
                        'fund_id': ic.fund_ids and ic.fund_ids[0].id or False,
                        'invest_construction_id': ic.id,
                        'invest_construction_phase_id': phase.id,
                    }
                    phase_sync.sync_budget_line_id = \
                        BudgetLine.create(budget_line_dict)
            phase.sync_phase_to_budget_line([fiscalyear_id])
        return True


class AccountBudgetLine(models.Model):
    _inherit = 'account.budget.line'

    planned_amount = fields.Float(
        string='Current Amount',  # Existing field, change label only
        help="Current Planned Amount"
    )
