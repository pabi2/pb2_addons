# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree
from openerp import api, fields, models, _
from openerp.osv.orm import setup_modifiers
from openerp.exceptions import except_orm, Warning, RedirectWarning


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    version = fields.Integer(
        string='Version',
        readonly=True,
        default=1,
        help="Indicate revision of the same budget plan. "
        "Only latest one is used",
    )
    latest_version = fields.Boolean(
        string='Current',
        readonly=True,
        default=True,
        # compute='_compute_latest_version',  TODO: determine version
        help="Indicate latest revision of the same plan.",
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
    )
    date_from = fields.Date(
        compute='_compute_date',
    )
    date_to = fields.Date(
        compute='_compute_date',
    )

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.multi
    def budget_validate(self):
        for budget in self:
            # On approval create analytic account auto, if not exists.
            budget.crossovered_budget_line.create_analytic_account_activity()
        return super(CrossoveredBudget, self).budget_validate()


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="['|', ('activity_group_id', '=', activity_group_id),"
        "('activity_group_id', '=', False)]"
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        required=True,
        domain="[('fiscalyear_id', '=', parent.fiscalyear_id)]",
    )
    date_from = fields.Date(
        compute='_compute_date',
    )
    date_to = fields.Date(
        compute='_compute_date',
    )

    @api.one
    @api.depends('period_id')
    def _compute_date(self):
        self.date_from = self.period_id.date_start
        self.date_to = self.period_id.date_stop

    @api.onchange('activity_id')
    def onchange_activity_id(self):
        self.activity_group_id = self.activity_id.activity_group_id

    @api.multi
    def create_analytic_account_activity(self):
        """ Create analytic account for those not been created """
        Analytic = self.env['account.analytic.account']
        for line in self:
            if line.activity_id:
                line.analytic_account_id = \
                    Analytic.create_matched_analytic(line)
            else:
                line.analytic_account_id = False
        return

