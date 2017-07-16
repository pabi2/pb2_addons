# -*- coding: utf-8 -*-
import time
from openerp.tools import float_compare
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.pabi_chartfield.models.chartfield import \
    CHART_VIEW_LIST, ChartField


class BudgetPolicy(models.Model):
    _name = 'budget.policy'
    _inherit = ['mail.thread']
    _description = 'Budget Policy'
    _order = 'id desc'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        default="/",
        copy=False,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        copy=False,
        default=lambda self: self.env.user,
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    revision = fields.Selection(
        lambda self: [(str(x), str(x))for x in range(13)],
        string='Revision',
        required=True,
        help="Revision 0 - 12, 0 is on on the fiscalyear open.",
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        readonly=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('ready', 'Ready'),
         ('not_ready', 'Not Ready'),
         ('done', 'Done'),
         ],
        string='Status',
        default='draft',
        track_visibility='onchange',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
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
    breakdown_count = fields.Integer(
        string='Breakdown Count',
        compute='_compute_breakdown_count',
    )
    # New Policy
    new_policy_amount = fields.Float(
        string='New Policy Overall',
        readonly=False,
        states={'done': [('readonly', True)]},
        help="Policy amount allocated overall. When done, "
    )
    # PLAN
    planned_amount = fields.Float(
        string='Planned Overall',
        compute='_compute_all',
        store=True,
    )
    # POLICY
    policy_amount = fields.Float(
        string='Policy Overall',
        compute='_compute_all',
        store=True,
    )
    line_ids = fields.One2many(
        'budget.policy.line',
        'policy_id',
        string='Policy Lines',
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    unit_base_line_ids = fields.One2many(
        'budget.policy.line',
        'policy_id',
        string='Policy Lines',
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    message = fields.Text(
        string='Messages',
        readonly=True,
    )
    # Relation to other model
    breakdown_ids = fields.One2many(
        'budget.breakdown',
        'policy_id',
        string='Breakdowns',
        readonly=True,
    )
    _sql_constraints = [
        ('uniq_revision', 'unique(chart_view, fiscalyear_id, revision)',
         'Duplicated revision of budget policy is not allowed!'),
    ]

    @api.multi
    @api.depends()
    def _compute_breakdown_count(self):
        Breakdown = self.env['budget.breakdown']
        for policy in self:
            policy.breakdown_count = len(Breakdown.search([('policy_id', '=',
                                                            policy.id)])._ids)

    @api.multi
    def action_open_breakdown(self):
        self.ensure_one()
        act = False
        if self.chart_view == 'unit_base':
            act = 'pabi_budget_plan.action_unit_base_breakdown_view'
        # elif self.chart_view == 'invest_asset':
        action = self.env.ref(act)
        result = action.read()[0]
        result.update({'domain': [('id', 'in', self.breakdown_ids.ids)]})
        return result

    @api.multi
    def _get_doc_number(self):
        self.ensure_one()
        _prefix = 'POLICY'
        _prefix2 = {'unit_base': 'UNIT',
                    'invest_asset': 'ASSET'}
        prefix2 = _prefix2[self.chart_view]
        name = '%s/%s/%s/V%s' % (_prefix, prefix2,
                                 self.fiscalyear_id.code, self.revision)
        return name

    @api.model
    def create(self, vals):
        res = super(BudgetPolicy, self).create(vals)
        res.name = res._get_doc_number()
        return res

    @api.model
    def default_get(self, fields):
        res = super(BudgetPolicy, self).default_get(fields)
        Fiscal = self.env['account.fiscalyear']
        if not res.get('fiscalyear_id', False):
            fiscals = Fiscal.search([
                ('date_start', '>', time.strftime('%Y-%m-%d'))],
                order='date_start')
            if fiscals:
                res['fiscalyear_id'] = fiscals[0].id
        chart_view = res.get('chart_view', False)
        if chart_view:
            revs = self.search([
                ('fiscalyear_id', '=', res['fiscalyear_id']),
                ('chart_view', '=', chart_view)]).mapped('revision')
            next_rev = revs and str(int(max(revs)) + 1) or '0'
            res['revision'] = next_rev
        return res

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        for rec in self:
            rec.date_from = rec.fiscalyear_id.date_start
            rec.date_to = rec.fiscalyear_id.date_stop

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

    @api.multi
    def generate_policy_line(self):
        for policy in self:
            policy.line_ids.unlink()
            lines = []
            # Unit Base
            if policy.chart_view == 'unit_base':
                # For Revision 0, compare with Budget Plan
                orgs = self.env['res.org'].search([])
                for org in orgs:
                    # Total plan for each org
                    plans = self.env['budget.plan.unit'].search([
                        ('org_id', '=', org.id),
                        ('fiscalyear_id', '=', policy.fiscalyear_id.id)])
                    planned_expense = sum(plans.mapped('planned_expense'))
                    vals = {'org_id': org.id,
                            'planned_amount': planned_expense, }
                    lines.append((0, 0, vals))
                policy.write({'unit_base_line_ids': lines})
            # Other structure...

    @api.multi
    def _validate_budget_plan_unit(self):
        """ Check relelated budget plan
        - Each org, the budget plan of all its section must be accepted
        """
        self.ensure_one()
        res = {'valid': True, 'message': ''}
        msg = []
        Section = self.env['res.section']
        Plan = self.env['budget.plan.unit']
        for org_policy in self.line_ids:
            org = org_policy.org_id
            msg.append('====================== %s ======================'
                       % (org.name_short,))
            # Active sections of this org
            sections = Section.search([('org_id', '=', org.id)])
            # Active plans of this org
            plans = Plan.search([
                ('fiscalyear_id', '=', self.fiscalyear_id.id),
                ('org_id', '=', org.id),
                ('state', '=', 'accept')])
            # All sections must have valid plans
            if len(sections) != len(plans):
                res['valid'] = False
                msg.append("Plan of following sections not accepted.")
                invalid_sections = sections.filtered(
                    lambda l: l.id not in plans.mapped('section_id').ids)
                for s in invalid_sections:
                    msg.append("* [%s] %s" % (s.code, s.name_short))
            else:
                msg.append("Ready...")
        res['message'] = '\n'.join(msg)
        return res

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_ready(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(
                    _('Before you proceed, please click button to '
                      '"Generate Policy Lines".'))
            result = {'valid': False, 'message': False}
            if rec.chart_view == 'unit_base':
                result = rec._validate_budget_plan_unit()
            else:
                raise ValidationError(
                    _('Cannot validate this budget structure'))
            if result['valid']:
                rec.write({'state': 'ready',
                           'message': False})
            else:
                rec.write({'state': 'not_ready',
                           'message': result['message']})

    @api.multi
    def action_done(self):
        for policy in self:
            if float_compare(policy.new_policy_amount,
                             policy.policy_amount, 2) != 0:
                raise ValidationError(_('Overall policy amount mismatch!'))
            if policy.chart_view == 'unit_base':
                policy.create_unit_base_policy_breakdown()
            else:
                raise ValidationError(
                    _('This action is not valid for this budget structure!'))
        self.write({'state': 'done'})

    @api.multi
    def create_unit_base_policy_breakdown(self):
        self.ensure_one()
        Breakdown = self.env['budget.breakdown']
        # For each policy line, create a breakdown
        for policy_line in self.unit_base_line_ids:
            # Create only if it has not been created before
            breakdowns = Breakdown.search([
                ('policy_line_id', '=', policy_line.id)])
            if breakdowns:
                continue
            # Not been created, make one.
            breakdown = Breakdown.create({'policy_line_id': policy_line.id})
            breakdown.generate_breakdown_line()


class BudgetPolicyLine(ChartField, models.Model):
    _name = 'budget.policy.line'
    _description = 'Budget Policy Detail'

    policy_id = fields.Many2one(
        'budget.policy',
        string='Budget Policy',
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )

    @api.multi
    @api.depends('policy_id')
    def _compute_name(self):
        for rec in self:
            chart_view = rec.policy_id.chart_view
            if chart_view == 'unit_base':
                rec.name = rec.org_id.name_short
            # Continue with other dimension
            else:
                rec.name = 'n/a'

    @api.multi
    def name_get(self):
        res = []
        for line in self:
            name = '%s - [Fy.%s Rev.%s]' % \
                (line.name,
                 line.policy_id.fiscalyear_id.code,
                 line.policy_id.revision)
            res.append((line.id, name))
        return res
