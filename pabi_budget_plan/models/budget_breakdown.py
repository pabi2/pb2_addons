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
        size=500,
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
    revision = fields.Integer(
        related='policy_line_id.policy_id.revision',
        string='Revision',
        store=True,
        readonly=True,
        help="Revision number",
    )
    planned_amount = fields.Float(
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
        domain=[('chart_view', '=', 'unit_base')],
    )
    invest_asset_line_ids = fields.One2many(
        'budget.breakdown.line',
        'breakdown_id',
        string='Invest Asset Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'invest_asset')],
    )
    personnel_line_ids = fields.One2many(
        'budget.breakdown.line',
        'breakdown_id',
        string='Personnel Breakdown Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[('chart_view', '=', 'personnel')],
    )
    message = fields.Text(
        string='Messages',
        readonly=True,
        size=1000,
    )
    _sql_constraints = [
        ('uniq_breakdown', 'unique(policy_line_id)',
         'Budget breakdown must have 1-1 relationship with budget policy!'),
    ]

    @api.multi
    def _compute_budget_count(self):
        # Tuning,
        # budget_count = len(breakdown.line_ids.mapped('budget_id'))
        self._cr.execute("""
            select breakdown_id, count(budget_id) count
            from budget_breakdown_line
            where budget_id is not null
            and breakdown_id in %s
            group by breakdown_id
        """, (tuple(self.ids), ))
        breakdown_budget_count = dict(self._cr.fetchall())
        for breakdown in self:
            breakdown.budget_count = \
                breakdown_budget_count.get(breakdown.id, 0)

    @api.multi
    def action_open_budget(self):
        self.ensure_one()
        _ACTION = {
            'unit_base': 'account_budget_activity.act_account_budget_view',
            'invest_asset':
            'pabi_chartfield.act_account_budget_view_invest_asset',
            'personnel': 'pabi_chartfield.act_account_budget_view_personnel',
        }
        action = self.env.ref(_ACTION[self.chart_view])
        result = action.read()[0]
        budget_ids = self.line_ids.mapped(lambda l: l.budget_id).ids
        result.update({'domain': [('id', 'in', budget_ids)]})
        return result

    @api.multi
    def _get_doc_number(self):
        self.ensure_one()
        _prefix = 'BREAKDOWN'
        _prefix2 = {'unit_base': 'UNIT',
                    'invest_asset': 'ASSET',
                    'personnel': 'PERSONNEL'}
        _prefix3 = {'unit_base': 'org_id',
                    'invest_asset': False,
                    'personnel': False}
        prefix2 = _prefix2[self.chart_view]
        obj = _prefix3[self.chart_view] and \
            self[_prefix3[self.chart_view]] or False
        prefix3 = obj and (obj.code or obj.name_short or obj.name) or 'NSTDA'
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
    @api.depends('line_ids', 'unit_base_line_ids',
                 'invest_asset_line_ids', 'personnel_line_ids')
    def _compute_all(self):
        for rec in self:
            if rec.unit_base_line_ids:
                lines = rec.unit_base_line_ids
            elif rec.invest_asset_line_ids:
                lines = rec.invest_asset_line_ids
            elif rec.personnel_line_ids:
                lines = rec.personnel_line_ids
            else:  # Fall back to basic
                lines = rec.line_ids
            rec.planned_amount = sum(lines.mapped('planned_amount'))
            rec.policy_amount = sum(lines.mapped('policy_amount'))
            rec.policy_diff = rec.policy_amount - rec.new_policy_amount

    @api.onchange('policy_line_id')
    def _onchange_policy_line_id(self):
        self.unit_base_line_ids = False
        self.invest_asset_line_ids = False

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

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
            # if not breakdown._validate_breakdown():
            #     continue
            breakdown.generate_budget_control()
            breakdown.write({'state': 'done'})

    # I think no need to check, if no line in control, just create one
    # @api.multi
    # def _validate_breakdown(self):
    #     """ Check relelated budget plan
    #     - If policy amount is not zero, at least there should be a plan line
    #     """
    #     self.ensure_one()
    #     res = {'valid': True, 'message': ''}
    #     msg = []
    #     if self.chart_view == 'unit_base':
    #         for line in self.unit_base_line_ids:
    #             if line.policy_amount:
    #                 plan_unit = line.budget_plan_id
    #                 if not plan_unit.plan_expense_line_ids:
    #                     res['valid'] = False
    #                     msg.append(
    #                       '%s - %s, do not have any plan line, policy amount'
    #                         ' is not allowed.' %
    #                       (plan_unit.name, plan_unit.section_id.name_short))
    #     res['message'] = '\n'.join(msg)
    #     if res['valid']:
    #         self.write({'message': False})
    #         return True
    #     else:
    #         self.write({'message': res['message']})
    #         return False

    @api.multi
    def generate_breakdown_line(self):
        for breakdown in self:
            _DICT = {'unit_base': ('budget.plan.unit',
                                   'org_id', 'section_id',
                                   'unit_base_line_ids'),
                     'invest_asset': ('budget.plan.invest.asset',
                                      False, 'org_id',
                                      'invest_asset_line_ids'),
                     'personnel': ('budget.plan.personnel',
                                   False, False,
                                   'personnel_line_ids'), }
            if breakdown.chart_view not in _DICT.keys():
                raise ValidationError(
                    _('This budget structure is not supported!'))

            breakdown.line_ids.unlink()
            lines = []
            company = self.env.user.company_id
            plan_model = _DICT[breakdown.chart_view][0]
            entity_field = _DICT[breakdown.chart_view][1]
            sub_entity_field = _DICT[breakdown.chart_view][2]
            breakdown_line_field = _DICT[breakdown.chart_view][3]
            entity_id = entity_field and breakdown[entity_field].id
            if not entity_field:
                entity_field = company.id
                entity_id = company.id

            Budget = self.env['account.budget']
            BudgetPlan = self.env[plan_model]
            plans = BudgetPlan.search([
                ('fiscalyear_id', '=', breakdown.fiscalyear_id.id),
                (entity_field, '=', entity_id),
                ('state', 'in', ('7_accept', '8_done'))])
            budgets = Budget.search([
                ('fiscalyear_id', '=', breakdown.fiscalyear_id.id),
                (entity_field, '=', entity_id),
                ('chart_view', '=', breakdown.chart_view)])
            # Existing budgets, sub_entity_dict, i.e.,  {seciton_id: budget_id}
            ent_bud_dict = {}  # {sub_entity_id: (budget_id, latest_policy)}
            for x in budgets:
                if sub_entity_field:
                    ent_bud_dict.update(
                        {x[sub_entity_field].id: (x.id,
                                                  x.policy_amount)})
                else:
                    # For personnel budget
                    ent_bud_dict.update({False: (x.id,
                                                 x.policy_amount)})
            # Create line from plans first, so this will also reference to plan
            for plan in plans:
                budget_plan_id = '%s,%s' % (BudgetPlan._name, plan.id)
                sub_entity_id = False
                vals = {}
                if sub_entity_field:
                    sub_entity_id = plan[sub_entity_field].id
                    vals.update({
                        sub_entity_field: sub_entity_id
                    })
                budget_id = False
                latest_policy_amount = False
                if ent_bud_dict.get(sub_entity_id, False):
                    budget_id = ent_bud_dict[sub_entity_id][0]
                    latest_policy_amount = ent_bud_dict[sub_entity_id][1]
                vals.update({
                    'budget_plan_id': budget_plan_id,
                    'budget_id': budget_id,
                    'policy_amount': latest_policy_amount,
                })
                lines.append((0, 0, vals))
            # Create line for budget that don't have plan, manual create
            if sub_entity_field:
                budgets = budgets.filtered(
                    lambda l: l[sub_entity_field]
                    not in plans.mapped(sub_entity_field))
                for budget in budgets:
                    vals = {
                        'budget_plan_id': False,
                        'budget_id': budget.id,
                        'policy_amount': budget.policy_amount,
                        sub_entity_field: budget[sub_entity_field].id
                    }
                    lines.append((0, 0, vals))
            breakdown.write({breakdown_line_field: lines,
                             'message': False})

        self.message_post(body=_('Regenerate Breakdown Lines, amounts reset!'))

    @api.multi
    def generate_budget_control(self):
        self.ensure_one()
        for line in self.line_ids:
            # Generate only line without budget_id yet
            if not line.budget_id:
                plan = line.budget_plan_id
                budget = plan.convert_to_budget_control()
                line.budget_id = budget
            # New policy, set is set to draft, if policy change from prev
            line.budget_id.policy_amount = line.policy_amount
            if line.budget_id.released_amount != line.policy_amount:
                line.budget_id.state = 'draft'
        self.write({'state': 'done'})

    @api.multi
    def export_report_budget_breakdown(self):
        self.ensure_one()
        # Create ID for budget.breakdown.line, so it can be imported.
        for line in self.line_ids:
            # This method create external_id if not yet available
            self.env['pabi.utils.xls'].get_external_id(line)
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
        [('budget.plan.unit', 'Budget Plan - Unit Based'),
         ('budget.plan.invest.asset', 'Budget Plan - Investment Asset'), ],
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
    released_amount = fields.Float(
        string='Released',
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

    @api.model
    def _get_planned_expense_hook(self, breakdown, budget_plan):
        planned_amount = budget_plan and budget_plan.planned_expense or 0.0
        return planned_amount

    @api.multi
    @api.depends('budget_plan_id', 'budget_id')
    def _compute_amount(self):
        for line in self:
            # From Budget Plan
            budget_plan = line.budget_plan_id
            line.planned_amount = \
                self._get_planned_expense_hook(line.breakdown_id, budget_plan)
            line.latest_policy_amount = line.budget_id and \
                line.budget_id.policy_amount or 0.0
            # From Budget Control
            line.future_plan = line.budget_id.future_plan
            line.past_consumed = line.budget_id.past_consumed
            line.rolling = line.budget_id.rolling
            line.released_amount = line.budget_id.released_amount

    @api.model
    def _change_amount_content(self, breakdown, new_amount):
        BREAKDOWN_LEVEL = {'unit_base': 'section_id',  # only 2 types
                           'invest_asset': 'org_id',
                           'personnel': False, }
        title = _('Policy amount change(s)')
        message = '<h3>%s</h3><ul>' % title
        for rec in self:
            field = BREAKDOWN_LEVEL[breakdown.chart_view]
            code = 'NSTDA'
            if field:
                obj = rec[field]
                code = obj.code or obj.name_short or obj.name
            message += _(
                '<li><b>%s</b>: %s → %s</li>'
            ) % (code,
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
