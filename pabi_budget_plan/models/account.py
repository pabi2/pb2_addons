# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class AccountFiscalyearBudgetLevel(models.Model):
    _inherit = 'account.fiscalyear.budget.level'

    release_follow_policy = fields.Boolean(
        string='Release by Policy',
        default=False,
        help="Change released amount with policy amount",
    )

    @api.onchange('budget_release')
    def _onchange_budget_release(self):
        self.release_follow_policy = False


class AccountFiscalyear(models.Model):
    _name = 'account.fiscalyear'
    _inherit = ['account.fiscalyear', 'mail.thread']

    budget_allocation_ids = fields.One2many(
        'budget.allocation',
        'fiscalyear_id',
        string='Budget Allocations',
    )
    overall_policy = fields.Float(
        string='NSTDA Policy',
    )
    latest_policy = fields.Float(
        string='Current NSTDA Policy',
        compute='_compute_latest_remain_policy',
    )
    remain_policy = fields.Float(
        string='Remain NSTDA Policy',
        compute='_compute_latest_remain_policy',
    )
    notes = fields.Text(
        string='Notes',
        size=1000,
    )

    @api.multi
    def _compute_latest_remain_policy(self):
        for rec in self.sudo():
            allocations = rec.budget_allocation_ids.sorted(
                key=lambda r: r.revision, reverse=True)
            amounts = {'amount_unit_base': 0.0,
                       'amount_project_base': 0.0,
                       'amount_invest_asset': 0.0,
                       'amount_invest_construction': 0.0,
                       'amount_personnel': 0.0,
                       }
            for line in allocations:
                for key in amounts.keys():
                    if not amounts[key]:
                        amounts[key] = line[key]
            rec.latest_policy = sum(amounts.values())
            rec.remain_policy = rec.overall_policy - rec.latest_policy

    @api.constrains('overall_policy')
    def _check_overall_policy(self):
        if self.overall_policy < 0.0:
            raise ValidationError(
                  _('NSTDA Policy field must no be negative value'))

    # def init(self, cr):
    #     env = Environment(cr, SUPERUSER_ID, {})
    #     Fiscal = env['account.fiscalyear']
    #     fiscals = Fiscal.search([])
    #     fiscals.generate_budget_allocations()
    #
    # @api.multi
    # def generate_budget_allocations(self):
    #     for fiscal in self:
    #         if not fiscal.budget_allocation_ids:
    #             lines = [(0, 0, {'revision': i}) for i in range(13)]
    #             fiscal.sudo().write({'budget_allocation_ids': lines})
    #
    # @api.model
    # def create(self, vals):
    #     fiscal = super(AccountFiscalyear, self).create(vals)
    #     fiscal.generate_budget_allocations()
    #     return fiscal
