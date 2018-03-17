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
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    revision = fields.Integer(
        string='Revision',
        required=True,
        help="Revision number",
        track_visibility='onchange',
    )
    revision_readonly = fields.Integer(
        related='revision',
        string='Revision',
        readonly=True,
    )
    chart_view = fields.Selection(
        CHART_VIEW_LIST,
        string='Budget View',
        readonly=True,
        track_visibility='onchange',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
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
        track_visibility='onchange',
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
        string='Budget Policy',
        required=True,
        readonly=False,
        states={'done': [('readonly', True)]},
        help="Policy amount allocated overall. When done, ",
        track_visibility='onchange',
    )
    # PLAN
    planned_amount = fields.Float(
        string='Planned Overall',
        compute='_compute_all',
        store=True,
    )
    # POLICY
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
    project_base_line_ids = fields.One2many(
        'budget.policy.line',
        'policy_id',
        string='Policy Lines',
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    personnel_line_ids = fields.One2many(
        'budget.policy.line',
        'policy_id',
        string='Policy Lines',
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    invest_asset_line_ids = fields.One2many(
        'budget.policy.line',
        'policy_id',
        string='Policy Lines',
        readonly=False,
        states={'done': [('readonly', True)]},
    )
    invest_construction_line_ids = fields.One2many(
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

    @api.model
    def _get_revision(self, fiscalyear_id, chart_view):
        existing_policies = self.search(
            [('chart_view', '=', chart_view),
             ('fiscalyear_id', '=', fiscalyear_id),
             ('id', '!=', self._context.get('active_id', False))],
            order='revision desc')
        revision = False
        if existing_policies:
            current_rev = existing_policies[0].revision
            if current_rev == 12:
                raise ValidationError(_('You have reached max revision!'))
            else:
                revision = existing_policies[0].revision + 1
        else:
            revision = 0
        return revision

    @api.model
    def _set_new_policy_amount(self, fiscalyear_id, chart_view, revision):
        _fields = {'unit_base': 'amount_unit_base',
                   'project_base': 'amount_project_base',
                   'personnel': 'amount_personnel',
                   'invest_asset': 'amount_invest_asset',
                   'invest_construction': 'amount_invest_construction'}
        alloc = self.env['budget.allocation'].search(
            [('fiscalyear_id', '=', self.fiscalyear_id.id),
             ('revision', '=', self.revision)])
        return alloc[_fields[chart_view]]

    @api.onchange('fiscalyear_id')
    def _onchange_fiscalyear_id(self):
        revision = self._get_revision(self.fiscalyear_id.id, self.chart_view)
        self.revision = revision
        new_policy_amount = self._set_new_policy_amount(self.fiscalyear_id.id,
                                                        self.chart_view,
                                                        self.revision)
        self.new_policy_amount = new_policy_amount

    @api.multi
    def _compute_breakdown_count(self):
        Breakdown = self.env['budget.breakdown']
        for policy in self:
            policy.breakdown_count = len(Breakdown.search([('policy_id', '=',
                                                            policy.id)])._ids)

    @api.multi
    def action_open_breakdown(self):
        self.ensure_one()
        _ACTION = {
            'unit_base': 'pabi_budget_plan.action_unit_base_breakdown_view',
            'invest_asset':
            'pabi_budget_plan.action_invest_asset_breakdown_view',
            'personnel':
            'pabi_budget_plan.action_personnel_breakdown_view',
        }
        if self.chart_view not in _ACTION.keys():
            raise ValidationError(_('No breakdown for this budget structure!'))
        action = self.env.ref(_ACTION[self.chart_view])
        result = action.read()[0]
        result.update({'domain': [('id', 'in', self.breakdown_ids.ids)]})
        return result

    @api.multi
    def _get_doc_number(self):
        self.ensure_one()
        _prefix = 'POLICY'
        _prefix2 = {'unit_base': 'UNIT',
                    'project_base': 'PROJECT',
                    'personnel': 'PERSONNEL',
                    'invest_asset': 'ASSET',
                    'invest_construction': 'CONSTRUCT'}
        prefix2 = _prefix2[self.chart_view]
        name = '%s/%s/%s/V%s' % (_prefix, prefix2,
                                 self.fiscalyear_id.code, self.revision)
        return name

    @api.model
    def create(self, vals):
        res = super(BudgetPolicy, self).create(vals)
        res.name = res._get_doc_number()
        res.generate_policy_line()
        return res

    @api.multi
    def write(self, vals):
        res = super(BudgetPolicy, self).write(vals)
        for rec in self:
            if rec.name != rec._get_doc_number():
                rec._write({'name': rec._get_doc_number()})
        return res

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise ValidationError(
                _('You can not delete policy whose status is "Done"!'))
        return super(BudgetPolicy, self).unlink()

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
        return res

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        for rec in self:
            rec.date_from = rec.fiscalyear_id.date_start
            rec.date_to = rec.fiscalyear_id.date_stop

    @api.multi
    @api.depends('new_policy_amount',
                 'line_ids',
                 'unit_base_line_ids',
                 'project_base_line_ids',
                 'personnel_line_ids',
                 'invest_asset_line_ids',
                 'invest_construction_line_ids',)
    def _compute_all(self):
        for rec in self:
            lines = False
            if rec.unit_base_line_ids:
                lines = rec.unit_base_line_ids
            if rec.invest_asset_line_ids:
                lines = rec.invest_asset_line_ids
            if rec.project_base_line_ids:
                lines = rec.project_base_line_ids
            if rec.personnel_line_ids:
                lines = rec.personnel_line_ids
            if rec.invest_construction_line_ids:
                lines = rec.invest_construction_line_ids
            else:  # Fall back to basic
                lines = rec.line_ids
            rec.planned_amount = sum(lines.mapped('planned_amount'))
            rec.policy_amount = sum(lines.mapped('policy_amount'))
            rec.policy_diff = rec.policy_amount - rec.new_policy_amount

    @api.multi
    def generate_policy_line(self):
        for policy in self:
            policy.line_ids.unlink()
            lines = []
            # 1st policy
            v0_lines = self.search(
                [('revision', '=', 0),
                 ('chart_view', '=', policy.chart_view),
                 ('fiscalyear_id', '=', policy.fiscalyear_id.id)]).line_ids
            # latest policy
            latest_lines = self.search(
                [('revision', '=', policy.revision - 1),
                 ('chart_view', '=', policy.chart_view),
                 ('fiscalyear_id', '=', policy.fiscalyear_id.id)]).line_ids

            _DICT = {
                'unit_base': ('budget.plan.unit',
                              'res.org', 'org_id',
                              'unit_base_line_ids'),
                'project_base': ('budget.plan.project',
                                 'res.program', 'program_id',
                                 'project_base_line_ids'),
                'personnel': ('budget.plan.personnel',
                              False, False,
                              'personnel_line_ids'),
                'invest_asset': ('budget.plan.invest.asset',
                                 False, False,
                                 'invest_asset_line_ids'),
                'invest_construction': ('budget.plan.invest.construction',
                                        False, False,
                                        'invest_construction_line_ids')
            }

            # Use company id, to handle case NSTDA level
            company = self.env.user.company_id

            plan_model = _DICT[policy.chart_view][0]
            model = _DICT[policy.chart_view][1]
            field = _DICT[policy.chart_view][2] or company.id
            policy_line = _DICT[policy.chart_view][3]
            entity_ids = model and \
                self.env[model].search([('special', '=', False)]).ids or \
                [company.id]

            # For Revision 0, compare with Budget Plan
            for entity_id in entity_ids:
                plan_dom = [('fiscalyear_id', '=', policy.fiscalyear_id.id),
                            (field, '=', entity_id)]
                # Total plan for each entity
                plans = self.env[plan_model].search(plan_dom)
                planned_expense = self._get_planned_expense_hook(policy, plans)
                vals = {'planned_amount': planned_expense, }
                if model:
                    vals.update({field: entity_id})
                # V0 and latest policy
                if policy.revision != 0:
                    v0_line = not model and v0_lines[0] or \
                        v0_lines.filtered(lambda l: l[field].id == entity_id)
                    lastest_line = not model and latest_lines[0] or \
                        latest_lines.filtered(
                            lambda l: l[field].id == entity_id)
                    v0_policy_amount = v0_line.policy_amount
                    latest_policy_amount = lastest_line.policy_amount
                    vals.update({
                        'v0_policy_amount': v0_policy_amount,
                        'latest_policy_amount': latest_policy_amount,
                        'policy_amount': latest_policy_amount,
                    })
                lines.append((0, 0, vals))
            policy.write({policy_line: lines})

        self.message_post(body=_('Regenerate Policy Lines, all amount reset!'))

    @api.model
    def _get_planned_expense_hook(self, plans):
        """ We have this hook as with internal charge module may change it """
        return sum(plans.mapped('planned_expense'))

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        _DICT = {
            'unit_base': ('budget.plan.unit', True),
            'project_base': ('budget.plan.project', False),
            'personnel': ('budget.plan.personnel', True),
            'invest_asset': ('budget.plan.invest.asset', True),
            'invest_construction': ('budget.plan.invest.construction', False),
        }
        for policy in self:
            policy._validate_policy_amount()
            if policy.chart_view in _DICT.keys():
                valid = policy._validate_policy()
                if not valid:
                    continue
                policy.write({'state': 'done'})
                # Create breakdown
                has_breakdown = _DICT[policy.chart_view][1]
                if has_breakdown:
                    policy._create_breakdown()
                # update all plans to done too
                model = _DICT[policy.chart_view][0]
                plans = self.env[model].search([
                    ('fiscalyear_id', '=', self.fiscalyear_id.id),
                    ('state', 'in', ('7_accept', '8_done'))])
                plans.write({'state': '8_done'})
            else:
                raise ValidationError(
                    _('This action is not valid for this budget structure!'))

    @api.multi
    def _validate_policy_amount(self):
        self.ensure_one()
        if float_compare(self.new_policy_amount,
                         self.policy_amount, 2) != 0:
            raise ValidationError(_('Overall policy amount mismatch!'))

    @api.multi
    def _validate_policy(self):
        """ Check relelated budget plan
        - Each entity (based in chart_view),
          the budget plan of all its sub_entity must be accepted
        """
        self.ensure_one()
        _DICT = {
            'unit_base': ('budget.plan.unit', 'org_id',  # Org as header
                          'res.section', 'section_id'),  # Section as line
            'project_base': ('budget.plan.project', 'program_id',
                             'res.program', 'program_id'),
            'personnel': ('budget.plan.personnel', False,
                          False, False),
            'invest_asset': ('budget.plan.invest.asset', False,
                             'res.org', 'org_id'),
            'invest_construction': ('budget.plan.invest.construction',
                                    'org_id', 'res.org', 'org_id'),
        }
        plan_model = _DICT[self.chart_view][0]
        entity_field = _DICT[self.chart_view][1]
        sub_entity_model = _DICT[self.chart_view][2]
        sub_entity_field = _DICT[self.chart_view][3]

        res = {'valid': True, 'message': ''}
        msg = []
        Plan = self.env[plan_model]
        for policy_line in self.line_ids:
            entity = entity_field and policy_line[entity_field] or False
            if not entity:
                entity = self.env.user.company_id
                entity_field = entity.id
            msg.append('====================== %s ======================'
                       % (entity.name,))
            # Active sections of this org
            field = entity_field
            if self.chart_view == 'project_base':  # Special Case
                field = 'id'
            # Active plans of this org
            plans = Plan.search([
                ('fiscalyear_id', '=', self.fiscalyear_id.id),
                (entity_field, '=', entity.id),
                ('state', 'in', ('7_accept', '8_done'))])
            # All entity must have valid plans
            if sub_entity_model:  # Except case Personnel
                sub_entities = self.env[sub_entity_model].search([
                    (field, '=', entity.id), ('special', '=', False)])
                if len(sub_entities) != len(plans):
                    res['valid'] = False
                    msg.append("Plan of following entity not accepted.")
                    subentity_ids = plans.mapped(sub_entity_field).ids
                    invalid_sections = sub_entities.filtered(
                        lambda l: l.id not in subentity_ids)
                    for s in invalid_sections:
                        msg.append("* %s" % s.display_name)
                else:
                    msg.append("Ready...")
            else:
                if len(plans) > 0:  # Case personnel budget
                    msg.append("Ready...")
                else:
                    msg.append("No budget plan.")

        res['message'] = '\n'.join(msg)

        if res['valid']:
            self.write({'message': False})
            return True
        else:
            self.write({'message': res['message']})
            return False

    @api.multi
    def _create_breakdown(self):
        self.ensure_one()
        Breakdown = self.env['budget.breakdown']
        # For each policy line, create a breakdown
        for policy_line in self.line_ids:
            # Create only if it has not been created before
            breakdowns = Breakdown.search([
                ('policy_line_id', '=', policy_line.id)])
            if breakdowns:
                continue
            # Not been created, make one.
            breakdown = Breakdown.create({'policy_line_id': policy_line.id})
            breakdown.generate_breakdown_line()
            # After breakdown created, if not change in amount, done it.
            if float_compare(breakdown.new_policy_amount,
                             breakdown.policy_amount, 2) == 0:
                breakdown.action_done()


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
    v0_policy_amount = fields.Float(
        string='V0 Policy Amount',
        readonly=True,
    )
    latest_policy_amount = fields.Float(
        string='Latest Policy Amount',
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
            elif chart_view == 'project_base':
                rec.name = rec.program_id.name_short
            elif chart_view == 'personnel':
                rec.name = 'NSTDA'
            elif chart_view == 'invest_asset':
                rec.name = 'NSTDA'
            elif chart_view == 'invest_construction':
                rec.name = 'NSTDA'
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

    @api.model
    def _change_amount_content(self, policy, new_amount):
        POLICY_LEVEL = {'unit_base': 'org_id',
                        'project_base': 'program_id',
                        'personnel': 'personnel_costcenter_id',
                        'invest_asset': 'org_id',
                        'invest_construction': 'org_id', }
        title = _('Policy amount change(s)')
        message = '<h3>%s</h3><ul>' % title
        for rec in self:
            obj = rec[POLICY_LEVEL[policy.chart_view]]
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
            for policy in self.mapped('policy_id'):
                lines = self.filtered(lambda l: l.policy_id == policy)
                new_amount = vals.get('policy_amount')
                message = lines._change_amount_content(policy, new_amount)
            if message:
                policy.message_post(body=message)
        return super(BudgetPolicyLine, self).write(vals)
