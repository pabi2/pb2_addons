# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, ChartField


class BudgetBreakdown(models.Model):
    _name = 'budget.breakdown'
    _inherit = ['mail.thread']
    _description = 'Budget Breakdown'
    _order = 'id desc'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        default='/',
        copy=False,
    )
    policy_line_id = fields.Many2one(
        'budget.policy.line',
        string='Budget Policy Line',
        required=True,
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        related='policy_line_id.policy_id.chart_view',
        string='Budget View',
        store=True,
        readonly=True,
    )
    revision = fields.Selection(
        lambda self: [(str(x), str(x))for x in range(13)],
        related='policy_line_id.policy_id.revision',
        string='Revision',
        store=True,
        readonly=True,
        help="Revision 0 - 12, 0 is on on the fiscalyear open.",
    )
    planned_overall = fields.Float(
        related='policy_line_id.planned_amount',
        string='Planned Overall',
        readonly=True,
        store=True,
    )
    policy_overall = fields.Float(
        related='policy_line_id.policy_amount',
        string='Policy Overall',
        readonly=True,
        store=True,
    )
    org_id = fields.Many2one(
        'res.org',
        related='policy_line_id.org_id',
        string='Org',
        readonly=True,
        store=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ],
        string='Status',
        default='draft',
        track_visibility='onchange',
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        related='policy_line_id.policy_id.fiscalyear_id',
        readonly=True,
        store=True,
        # readonly=True,
    )
    date_from = fields.Date(
        string='Start Date',
        related='policy_line_id.policy_id.date_from',
        readonly=True,
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        related='policy_line_id.policy_id.date_to',
        readonly=True,
        store=True,
    )
    line_ids = fields.One2many(
        'budget.breakdown.line',
        'breakdown_id',
        string='Policy Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    unit_base_line_ids = fields.One2many(
        'budget.breakdown.line',
        'breakdown_id',
        string='Unit Based Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    # budget_control_count = fields.Integer(
    #     compute="_count_budget_control",
    #     string="Budget Controls",
    #     readonly=True,
    #     copy=False,
    # )
    _sql_constraints = [
        ('uniq_breakdown', 'unique(policy_line_id)',
         'Budget breakdown must have 1-1 relationship with budget policy!'),
    ]

    @api.multi
    def action_done(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(
                    _('No lines.\nPlease generate breakdown lines!'))
            result = {'valid': False, 'message': False}
            if rec.chart_view == 'unit_base':
                result = rec._validate_budget_plan_unit()
            else:
                raise ValidationError(
                    _('Cannot validate this budget structure'))
            if result['valid']:
                rec.state = 'ready'
            else:
                rec.write({'state': 'not_ready',
                           'message': result['message']})
        self.write({'state': 'done'})

    # @api.depends()
    # def _count_budget_control(self):
    #     for breakdown in self:
    #         counts = len(self.env['account.budget'].search(
    #             [('ref_breakdown_id', '=', breakdown.id)])._ids)
    #         breakdown.budget_control_count = counts
    #
    # @api.multi
    # @api.depends('fiscalyear_id')
    # def _compute_date(self):
    #     for rec in self:
    #         rec.date_from = rec.fiscalyear_id.date_start
    #         rec.date_to = rec.fiscalyear_id.date_stop
    #
    # @api.multi
    # def get_budget_controls(self):
    #     self.ensure_one()
    #     budget_controls =\
    #         self.env['account.budget'].search(
    #             [('ref_breakdown_id', '=', self.id)])
    #     act = 'account_budget_activity.act_account_budget_view'
    #     action = self.env.ref(act)
    #     result = action.read()[0]
    #     dom = [('id', 'in', budget_controls.ids)]
    #     result.update({'domain': dom})
    #     return result

    @api.multi
    def generate_breakdown_line(self):
        for rec in self:
            rec.line_ids.unlink()
            lines = []
            # Unit Base
            if rec.chart_view == 'unit_base':
                # For Revision 0, compare with Budget Plan
                plans = self.env['budget.plan.unit'].search([
                    ('fiscalyear_id', '=', rec.fiscalyear_id.id),
                    ('org_id', '=', rec.org_id.id),
                    ('state', '=', 'accept')])
                for plan in plans:
                    vals = {'budget_plan_unit_id': plan.id,  # for revision 0
                            'section_id': plan.section_id.id,
                            'planned_amount': plan.planned_expense,
                            }
                    lines.append((0, 0, vals))
                rec.write({'unit_base_line_ids': lines})
            # Other structure...

    @api.multi
    def convert_unit_base_plan_to_control(self):
        for line in self.line_ids:
            x = 1/0


class BudgetBreakdownLine(ChartField, models.Model):
    _name = 'budget.breakdown.line'
    _description = 'Budget Breakdown Lines'

    breakdown_id = fields.Many2one(
        'budget.breakdown',
        string='Budget Breakdown',
        index=True,
        ondelete='cascade',
    )
    budget_plan_unit_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan - Unit Base',
        readonly=True,
    )
    planned_amount = fields.Float(
        related='budget_plan_unit_id.planned_expense',
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )
