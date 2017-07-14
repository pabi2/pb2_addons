# -*- coding: utf-8 -*-
import time
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
    _sql_constraints = [
        ('uniq_revision', 'unique(chart_view, fiscalyear_id, revision)',
         'Duplicated revision of budget policy is not allowed!'),
    ]

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
    @api.depends('line_ids')
    def _compute_all(self):
        for rec in self:
            rec.planned_amount = sum(rec.line_ids.mapped('planned_amount'))
            rec.policy_amount = sum(rec.line_ids.mapped('policy_amount'))

    @api.multi
    def generate_policy_line(self):
        for rec in self:
            rec.line_ids.unlink()
            lines = []
            # Unit Base
            if rec.chart_view == 'unit_base':
                # For Revision 0, compare with Budget Plan
                orgs = self.env['res.org'].search([])
                for org in orgs:
                    # Total plan for each org
                    plans = self.env['budget.plan.unit'].search([
                        ('org_id', '=', org.id),
                        ('fiscalyear_id', '=', rec.fiscalyear_id.id)])
                    planned_expense = sum(plans.mapped('planned_expense'))
                    vals = {'org_id': org.id,
                            'planned_amount': planned_expense, }
                    lines.append((0, 0, vals))
                rec.write({'unit_base_line_ids': lines})
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
                    _('No lines.\nPlease generate policy lines!'))
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

    @api.multi
    def action_done(self):
        for rec in self:
            if rec.chart_view == 'unit_base':
                rec.create_unit_base_policy_breakdown()
            else:
                raise ValidationError(
                    _('This action is not valid for this budget structure!'))
        self.write({'state': 'done'})

    @api.multi
    def create_unit_base_policy_breakdown(self):
        self.ensure_one()
        Breakdown = self.env['budget.breakdown']
        BreakdownLine = self.env['budget.breakdown.line']
        Unit = self.env['budget.plan.unit']
        domain = [('fiscalyear_id', '=', self.fiscalyear_id.id),
                  ('ref_budget_policy_id', '=', self.id)]
        Breakdown_search = Breakdown.search(domain +
                                            [('chart_view', '=', 'unit_base'),
                                             ('state', '!=', 'cancel')])
        if Breakdown_search:
            raise ValidationError(_('Breakdowns already created.'))
        for org_policy in self.line_ids:
            # ref_policy_id = org_policy.policy_id.ref_policy_id
            # ref_policy_breakdown = False
            # if ref_policy_id:
            #     ref_policy_breakdown = Breakdown.search(
            #         [('ref_budget_policy_id', '=', ref_policy_id.id),
            #          ('org_id', '=', org_policy.org_id.id)])
            #     if ref_policy_breakdown:
            #         ref_policy_breakdown = ref_policy_breakdown.id
            vals = {  # TODO: Sequence Numbering ???
                'name': org_policy.org_id.name,
                'chart_view': self.chart_view,
                'org_id': org_policy.org_id.id,
                'planned_overall': org_policy.planned_amount,
                'policy_overall': org_policy.policy_amount,
                'fiscalyear_id': self.fiscalyear_id.id,
                'ref_budget_policy_id': self.id,
                'revision': self.revision,
                # 'ref_breakdown_id': ref_policy_breakdown,
            }
            breakdown = Breakdown.create(vals)
            plans = Unit.search(
                [('state', '=', 'accept_corp'),
                 ('fiscalyear_id', '=', breakdown.fiscalyear_id.id),
                 ('org_id', '=', breakdown.org_id.id)])
            for plan in plans:
                vals = self._prepare_breakdown_line('unit', plan, breakdown)
                BreakdownLine.create(vals)
            # Upon creation of breakdown, ensure data integrity
            sum_planned_amount = sum([l.planned_amount
                                      for l in breakdown.line_ids])
            if breakdown.planned_overall != sum_planned_amount:
                raise ValidationError(
                    _('For policy breakdown of Org: %s, \n'
                      'the overall planned amount is not equal to the '
                      'sum of all its sections') % (breakdown.org_id.name))


class BudgetPolicyLine(ChartField, models.Model):
    _name = 'budget.policy.line'
    _description = 'Budget Policy Detail'

    policy_id = fields.Many2one(
        'budget.policy',
        string='Budget Policy',
        ondelete='cascade',
        index=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    policy_amount = fields.Float(
        string='Policy Amount',
    )
