# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, CHART_VIEW_FIELD, ChartField


class BudgetFiscalPolicyBreakdown(models.Model):
    _name = 'budget.fiscal.policy.breakdown'
    _description = 'Fiscal Year Budget Policy'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
        readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        required=True,
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
    )
    creating_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self._uid,
        readonly=True,
    )
    validating_user_id = fields.Many2one(
        'res.users',
        copy=False,
        string='Validating User',
        readonly=True,
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=fields.Date.today(),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_confirm = fields.Date(
        string='Confirmed Date',
        copy=False,
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        readonly=True,
        store=True,
    )
    planned_overall = fields.Float(
        string='Planned Overall',
        required=True,
        readonly=True,
    )
    policy_overall = fields.Float(
        string='Policy Overall',
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        'budget.fiscal.policy.breakdown.line',
        'breakdown_id',
        string='Policy Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    ref_budget_policy_id = fields.Many2one(
        'budget.fiscal.policy',
        string='Ref Budget Policy',
        readonly=True,
    )

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_confirm(self):
        self.ensure_one()
        sum_policy_amount = sum([l.policy_amount for l in self.line_ids])
        if self.policy_overall != sum_policy_amount:
            raise UserError(_('Overall policy amount is not full filled'))
        self.write({
            'state': 'confirm',
            'validating_user_id': self._uid,
            'date_confirm': fields.Date.today(),
        })
        return True

    @api.multi
    def _check_data_integrity(self):
        self.ensure_one()
        # Overall and sum of lines must be equal
        sum_planned_amount = sum([l.planned_amount for l in self.line_ids])
        if self.planned_overall != sum_planned_amount:
            raise ValidationError(
                _('For policy breakdown of Org: %s, \n'
                  'the overall planned amount is not equal to the '
                  'sum of all its sections') % (self.org_id.name))


class BudgetFiscalPolicyBreakdownLine(ChartField, models.Model):
    _name = 'budget.fiscal.policy.breakdown.line'
    _description = 'Fiscal year Budget Policy Breakdown Lines'

    breakdown_id = fields.Many2one(
        'budget.fiscal.policy.breakdown',
    )
    budget_plan_unit_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan - Unit Base',
        readonly=True,
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        required=False,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )
