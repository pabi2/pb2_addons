# -*- coding: utf-8 -*-
from openerp.tools import float_compare
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
        track_visibility='onchange',
    )
    policy_id = fields.Many2one(
        'budget.policy',
        string='Budget Policy',
        related='policy_line_id.policy_id',
        store=True,
        readonly=True,
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
    planned_amount = fields.Float(
        related='policy_line_id.planned_amount',
        string='Planned Overall',
        compute='_compute_all',
        store=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
        compute='_compute_all',
        store=True,
    )
    policy_diff = fields.Float(
        string='Diff Amount',
        compute='_compute_all',
        store=True,
    )
    new_policy_amount = fields.Float(
        related='policy_line_id.policy_amount',
        string='Budget Policy',
        readonly=True,
        store=True,
        help="Policy amount allowcated by cooperate."
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
        track_visibility='onchange',
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
    budget_count = fields.Integer(
        string='Budget Count',
        compute='_compute_budget_count',
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
    _sql_constraints = [
        ('uniq_breakdown', 'unique(policy_line_id)',
         'Budget breakdown must have 1-1 relationship with budget policy!'),
    ]

    @api.multi
    @api.depends()
    def _compute_budget_count(self):
        for breakdown in self:
            breakdown.budget_count = \
                len(breakdown.line_ids.mapped(lambda l: l.budget_id))

    @api.multi
    def action_open_budget(self):
        self.ensure_one()
        act = False
        if self.chart_view == 'unit_base':
            act = 'account_budget_activity.act_account_budget_view'
        # elif self.chart_view == 'invest_asset':
        action = self.env.ref(act)
        result = action.read()[0]
        budget_ids = self.line_ids.mapped(lambda l: l.budget_id).ids
        result.update({'domain': [('id', 'in', budget_ids)]})
        return result

    @api.multi
    def _get_doc_number(self):
        self.ensure_one()
        _prefix = 'BREAKDOWN'
        _prefix2 = {'unit_base': 'UNIT',
                    'invest_asset': 'ASSET'}
        _prefix3 = {'unit_base': 'org_id',
                    'invest_asset': 'org_id'}
        prefix2 = _prefix2[self.chart_view]
        obj = self[_prefix3[self.chart_view]]
        prefix3 = obj.code or obj.name_short or obj.name
        name = '%s/%s/%s/%s/V%s' % (_prefix, prefix2, self.fiscalyear_id.code,
                                    prefix3, self.revision)
        return name

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise ValidationError(
                _('You can not delete breakdown whose status is "Done"!'))
        return super(BudgetBreakdown, self).unlink()

    @api.model
    def create(self, vals):
        res = super(BudgetBreakdown, self).create(vals)
        res.name = res._get_doc_number()
        return res

    @api.multi
    def write(self, vals):
        res = super(BudgetBreakdown, self).write(vals)
        for rec in self:
            if rec.name != rec._get_doc_number():
                rec._write({'name': rec._get_doc_number()})
        return res

    @api.multi
    @api.depends('line_ids', 'unit_base_line_ids')
    def _compute_all(self):
        for rec in self:
            lines = False
            if rec.unit_base_line_ids:
                lines = rec.unit_base_line_ids
            else:  # Fall back to basic
                lines = rec.line_ids
            rec.planned_amount = sum(lines.mapped('planned_amount'))
            rec.policy_amount = sum(lines.mapped('policy_amount'))
            rec.policy_diff = rec.policy_amount - rec.new_policy_amount

    @api.onchange('policy_line_id')
    def _onchange_policy_line_id(self):
        self.unit_base_line_ids = False

    @api.multi
    def action_done(self):
        for breakdown in self:
            if float_compare(breakdown.new_policy_amount,
                             breakdown.policy_amount, 2) != 0:
                raise ValidationError(_('Overall policy amount mismatch!'))
            if not breakdown.line_ids:
                raise ValidationError(
                    _('Before you proceed, please click button to '
                      '"Generate Breakdown Lines".'))
            breakdown.generate_budget_control()
        self.write({'state': 'done'})

    @api.multi
    def _generate_breakdown_line_unit_base(self):
        for breakdown in self:
            if breakdown.chart_view != 'unit_base':
                raise ValidationError(_('Not a unit based breakdown!'))
            breakdown.line_ids.unlink()
            lines = []
            Budget = self.env['account.budget']
            BudgetPlanUnit = self.env['budget.plan.unit']
            plans = BudgetPlanUnit.search([
                ('fiscalyear_id', '=', breakdown.fiscalyear_id.id),
                ('org_id', '=', breakdown.org_id.id),
                ('state', '=', 'accept')])
            budgets = Budget.search([
                ('fiscalyear_id', '=', breakdown.fiscalyear_id.id),
                ('org_id', '=', breakdown.org_id.id),
                ('chart_view', '=', breakdown.chart_view)])
            # Existing budgets, get section dict {seciton_id: budget_id}
            sec_bud_dict = dict([(x.section_id.id, x.id) for x in budgets])
            # Create line from plans first
            for plan in plans:
                budget_plan_id = '%s,%s' % (BudgetPlanUnit._name, plan.id)
                section_id = plan.section_id.id
                vals = {
                    'budget_plan_id': budget_plan_id,
                    'budget_id': sec_bud_dict.get(section_id, False),
                    'section_id': plan.section_id.id,
                }
                lines.append((0, 0, vals))
            # Create line for budget that don't have plan, manual create
            budgets = budgets.filtered(lambda l: l.section_id
                                       not in plans.mapped('section_id'))
            for budget in budgets:
                vals = {
                    'budget_plan_id': False,
                    'budget_id': budget.id,
                    'section_id': budget.section_id.id,
                }
                lines.append((0, 0, vals))
            breakdown.write({'unit_base_line_ids': lines})

    @api.multi
    def generate_breakdown_line(self):
        # Unit Base
        breakdowns = self.filtered(lambda l: l.chart_view == 'unit_base')
        if breakdowns:
            breakdowns._generate_breakdown_line_unit_base()
        # Other structure...

    @api.multi
    def generate_budget_control(self):
        self.ensure_one()
        for line in self.line_ids:
            # Generate only line without budget_id yet
            if not line.budget_id:
                plan = line.budget_plan_id
                budget = plan.convert_to_budget_control()
                line.budget_id = budget
            # New policy, set is set to draft
            line.budget_id.write({'state': 'draft',
                                  'policy_amount': line.policy_amount})
        self.write({'state': 'done'})

    @api.multi
    def export_report_budget_breakdown(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_budget_breakdown',
        }


class BudgetBreakdownLine(ChartField, models.Model):
    _name = 'budget.breakdown.line'
    _description = 'Budget Breakdown Lines'

    breakdown_id = fields.Many2one(
        'budget.breakdown',
        string='Budget Breakdown',
        index=True,
        ondelete='cascade',
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        related='breakdown_id.chart_view',
        string='Budget View',
        store=True,
        readonly=True,
    )
    # References
    budget_plan_id = fields.Reference(
        [('budget.plan.unit', 'Budget Plan - Unit Based'), ],
        string='Budget Plan',
        readonly=True,
        ondelete='set null',
    )
    budget_id = fields.Many2one(
        'account.budget',
        string='Budget Control',
        readonly=True,
        ondelete='set null'
    )
    budget_state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Controlled')],
        related='budget_id.state',
        string='Budget Status',
        store=True,
        readnly=True,
    )
    # --
    past_consumed = fields.Float(
        string='Consumed',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    future_plan = fields.Float(
        string='Future',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    rolling = fields.Float(
        string='Rolling',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    latest_policy_amount = fields.Float(
        string='Latest Policy Amount',
        compute='_compute_amount',
        store=True,
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )

    @api.multi
    @api.depends('breakdown_id')
    def _compute_amount(self):
        for line in self:
            line.planned_amount = line.budget_plan_id.planned_expense or 0.0
            line.latest_policy_amount = line.budget_id.policy_amount or 0.0

    @api.model
    def _change_amount_content(self, breakdown, new_amount):
        BREAKDOWN_LEVEL = {'unit_base': 'section_id',  # only 2 types
                           'invest_asset': 'org_id', }
        title = _('Policy amount change(s)')
        message = '<h3>%s</h3><ul>' % title
        for rec in self:
            obj = rec[BREAKDOWN_LEVEL[breakdown.chart_view]]
            message += _(
                '<li><b>%s</b>: %s → %s</li>'
            ) % (obj.code or obj.name_short or obj.name,
                 '{:,.2f}'.format(rec.policy_amount),
                 '{:,.2f}'.format(new_amount), )
            message += '</ul>'
        return message

    @api.multi
    def write(self, vals):
        # Grouping by Policy
        if 'policy_amount' in vals:
            for breakdown in self.mapped('breakdown_id'):
                lines = self.filtered(lambda l: l.breakdown_id == breakdown)
                new_amount = vals.get('policy_amount')
                message = lines._change_amount_content(breakdown, new_amount)
            if message:
                breakdown.message_post(body=message)
        return super(BudgetBreakdownLine, self).write(vals)
