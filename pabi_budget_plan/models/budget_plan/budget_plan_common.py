# -*- coding: utf-8 -*-
from openerp import tools
from openerp import fields, api, _
from openerp.addons.pabi_chartfield.models.chartfield import ChartField
from openerp.exceptions import ValidationError

# This is the most detailed stats for any budget plan structure.
# We make it common, but not necessary to use all of them
_STATE = [('1_draft', 'Draft'),
          ('2_submit', 'Submitted'),  # draft
          ('3_approve', 'Approved'),  # submit
          ('4_cancel', 'Cancelled'),  # draft,submit
          ('5_reject', 'Rejected'),   # submit,approve
          ('6_verify', 'Verified'),   # approve
          ('7_accept', 'Accepted'),   # verify
          ('8_done', 'Done'),   # verify
          # Accepted by Cooperate
          ]


class Common(object):

    @api.model
    def search_args(self, args):
        section = self.env.user.partner_id.employee_id.section_id
        if self._context.get('my_org_plans', False):
            args += [('org_id', '=', section.org_id.id)]
        if self._context.get('my_section_plans', False):
            args += [('section_id', '=', section.id)]
        if self._context.get('my_division_plans', False):
            args += [('division_id', '=', section.division_id.id)]
        if self._context.get('this_year_plans', False):
            current_fiscalyear = \
                self.env['account.period'].find().fiscalyear_id
            args += [('fiscalyear_id', '=', current_fiscalyear.id)]
        return args


class BPCommon(Common):

    """ Budget Plan Header, no Chartfield here """
    name = fields.Char(
        string='Number',
        required=True,
        readonly=True,
        default="/",
        copy=False,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
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
        required=True,
        # readonly=True,
        default=lambda self: self.env['account.period'].find().fiscalyear_id,
        track_visibility='onchange',
    )
    date_from = fields.Date(
        string='Start Date',
        compute='_compute_date',
        store=True,
    )
    date_to = fields.Date(
        string='End Date',
        compute='_compute_date',
        store=True,
    )
    planned_revenue = fields.Float(
        string='Total Revenue Plan',
        compute='_compute_planned_overall',
        store=True,
        help="All Revenue",
        track_visibility='onchange',
    )
    planned_expense = fields.Float(
        string='Total Expense Plan',
        compute='_compute_planned_overall',
        store=True,
        help="All Expense",
        track_visibility='onchange',
    )
    planned_overall = fields.Float(
        string='Total Planned',
        compute='_compute_planned_overall',
        store=True,
        help="All Revenue - All Expense",
        track_visibility='onchange',
    )
    state = fields.Selection(
        _STATE,
        string='Status',
        default='1_draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )

    @api.multi
    def write(self, vals):
        if 'state' in vals:
            for rec in self:
                if not rec.user_id:
                    vals['user_id'] = self.env.user.id
        return super(BPCommon, self).write(vals)

    @api.model
    def _get_doc_number(self, fiscalyear_id, model, res_id=False, code=False):
        _prefix = 'PLAN'
        fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
        if res_id:
            res = self.env[model].browse(res_id)
            code = res.code or res.name_short or res.name
        return '%s/%s/%s' % (_prefix, fiscal.code, code)

    @api.multi
    @api.depends('plan_line_ids',
                 'plan_line_ids.planned_amount',
                 'plan_line_ids.budget_method')
    def _compute_planned_overall(self):
        for rec in self:
            lines = rec.plan_line_ids
            exp_lines = lines.filtered(lambda l: l.budget_method == 'expense')
            rev_lines = lines.filtered(lambda l: l.budget_method == 'revenue')
            rec.planned_expense = sum(exp_lines.mapped('planned_amount'))
            rec.planned_revenue = sum(rev_lines.mapped('planned_amount'))
            rec.planned_overall = rec.planned_revenue - rec.planned_expense

    @api.multi
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        for rec in self:
            rec.date_from = rec.fiscalyear_id.date_start
            rec.date_to = rec.fiscalyear_id.date_stop

    @api.multi
    def action_draft(self):
        self.write({'state': '1_draft'})

    @api.multi
    def action_submit(self):
        self.write({'state': '2_submit'})

    @api.multi
    def action_approve(self):
        self.write({'state': '3_approve'})

    @api.multi
    def action_cancel(self):
        self.write({'state': '4_cancel'})

    @api.multi
    def action_reject(self):
        self.write({'state': '5_reject'})

    @api.multi
    def action_verify(self):
        self.write({'state': '6_verify'})

    @api.multi
    def action_accept(self):
        self.write({'state': '7_accept'})

    @api.multi
    def action_done(self):
        self.write({'state': '8_done'})

    @api.model
    def _prepare_copy_fields(self, source_model, target_model):
        src_fields = [f for f, _x in source_model._fields.iteritems()]
        no_fields = [
            'id', 'state', 'display_name', '__last_update', 'state'
            'write_date', 'create_date', 'create_uid', 'write_uid',
            'date', 'date_from', 'date_to',
            'creating_user_id',
        ]
        trg_fields = [f for f, _x in target_model._fields.iteritems()]
        return list((set(src_fields) & set(trg_fields)) - set(no_fields))

    @api.model
    def _convert_plan_to_budget_control(self, active_id,
                                        head_src_model,
                                        line_src_model):
        head_trg_model = self.env['account.budget']
        line_trg_model = self.env['account.budget.line']
        header_fields = self._prepare_copy_fields(head_src_model,
                                                  head_trg_model)
        line_fields = self._prepare_copy_fields(line_src_model,
                                                line_trg_model)
        plan = self.browse(active_id)
        budget = {}
        for key in header_fields:
            if key in plan._columns:
                if plan._columns[key]._type in ('one2many', 'many2many'):
                    continue
            budget.update({key: (hasattr(plan[key], '__iter__') and
                           plan[key].id or plan[key])})
        budget_lines = []
        for line in plan.plan_line_ids:
            budget_line_vals = {}
            for key in line_fields:
                budget_line_vals.update({
                    key: (hasattr(line[key], '__iter__') and
                          line[key].id or line[key])
                })
            budget_lines.append((0, 0, budget_line_vals))
        budget['budget_line_ids'] = budget_lines
        return self.env['account.budget'].create(budget)

    @api.multi
    def compute_prev_fy_performance(self):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        PrevFY = self.env['%s.prev.fy.view' % self._name]
        PrevFY._fill_prev_fy_performance(self)  # self = plans


class BPLCommon(ChartField, Common):

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string="Activity Group",
        required=True,
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
        required=True,
        default='expense',
        help="Specify whether the budget plan line is of Revenue or Expense. "
        "Revenue is for Unit Based only."
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        related='plan_id.fiscalyear_id',
        string='Fiscal Year',
        store=True,
    )
    name = fields.Char(
        string='Description',
    )
    state = fields.Selection(
        _STATE,
        string='Status',
        related='plan_id.state',
        store=True,
    )
    description = fields.Text(
        string="Description",
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )


class BPLMonthCommon(BPLCommon):

    m0 = fields.Float(
        string='Commit Carry Over',
        required=False,
    )
    m1 = fields.Float(
        string='Oct',
        required=False,
    )
    m2 = fields.Float(
        string='Nov',
        required=False,
    )
    m3 = fields.Float(
        string='Dec',
        required=False,
    )
    m4 = fields.Float(
        string='Jan',
        required=False,
    )
    m5 = fields.Float(
        string='Feb',
        required=False,
    )
    m6 = fields.Float(
        string='Mar',
        required=False,
    )
    m7 = fields.Float(
        string='Apr',
        required=False,
    )
    m8 = fields.Float(
        string='May',
        required=False,
    )
    m9 = fields.Float(
        string='Jun',
        required=False,
    )
    m10 = fields.Float(
        string='Jul',
        required=False,
    )
    m11 = fields.Float(
        string='Aug',
        required=False,
    )
    m12 = fields.Float(
        string='Sep',
        required=False,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        store=True,
    )

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            rec.planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                      rec.m5, rec.m6, rec.m7, rec.m8,
                                      rec.m9, rec.m10, rec.m11, rec.m12
                                      ])


class PrevFYCommon(object):
    """ Super class for all budget plan previous performance views """

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        readonly=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        readonly=True,
    )
    planned = fields.Float(
        string='Planned',
        readonly=True,
    )
    released = fields.Float(
        string='Released',
        readonly=True,
    )
    pr_commit = fields.Float(
        string='PR Commit',
        readonly=True,
    )
    po_commit = fields.Float(
        string='PO Commit',
        readonly=True,
    )
    exp_commit = fields.Float(
        string='EX Commit',
        readonly=True,
    )
    all_commit = fields.Float(
        string='All Commit',
        readonly=True,
    )
    actual = fields.Float(
        string='Actual',
        readonly=True,
    )
    consumed = fields.Float(
        string='Consumed',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    carry_forward = fields.Float(
        string='Carry Forward',
        readonly=True,
    )

    _base_prev_fy_sql = """
        select max(id) id, fiscalyear_id, fund_id, %s,
            sum(planned_amount) as planned,
            sum(released_amount) as released,
            sum(amount_pr_commit) pr_commit,
            sum(amount_po_commit) po_commit,
            sum(amount_exp_commit) exp_commit,
            sum(coalesce(amount_pr_commit, 0.0) +
                coalesce(amount_po_commit, 0.0) +
                coalesce(amount_exp_commit, 0.0)) all_commit,
            sum(amount_actual) actual,
            sum(amount_consumed) consumed,
            sum(amount_balance) balance,
            sum(coalesce(released_amount, 0.0)
                - coalesce(amount_actual, 0.0)) carry_forward
        from budget_monitor_report
        where chart_view = '%s'
            and budget_method = 'expense'
        group by fiscalyear_id, fund_id, %s
    """

    def init(self, cr):
        # Additional fields for this budget structure
        ex = ', '.join(self._ex_view_fields)
        sql = self._base_prev_fy_sql % (ex, self._chart_view, ex)
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("create or replace view %s as (%s)" % (self._table, sql))

    @api.model
    def _fill_prev_fy_performance(self, plans):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        Fiscal = self.env['account.fiscalyear']
        plans.mapped('plan_line_ids').unlink()
        for plan in plans:
            prev_fy = Fiscal.search(
                [('date_stop', '<', plan.fiscalyear_id.date_start)],
                order='date_stop desc', limit=1)
            if not prev_fy:
                return
            ctx = {'plan_fiscalyear_id': plan.fiscalyear_id.id,
                   'prev_fiscalyear_id': prev_fy.id}
            # Lookup for previous year performance only
            domain = []
            # filter: 1 = Previous Year Only, 2 = Prev and Current Planning
            if self._filter_fy not in (False, 1, 2):
                raise ValidationError(_('_filter_fy must be False, 1, 2'))
            if self._filter_fy == 1:
                domain = [('fiscalyear_id', '=', prev_fy.id)]
            elif self._filter_fy == 2:
                domain = ['|', ('fiscalyear_id', '=', prev_fy.id),
                          ('fiscalyear_id', '=', plan.fiscalyear_id.id)]
            for field in self._ex_domain_fields:
                domain.append((field, '=', plan[field].id))
            if self._ex_active_domain:
                domain += self._ex_active_domain
            # Prepare prev fy plan lines
            lines = self.search(domain)
            plan_lines = lines.with_context(ctx)._prepare_prev_fy_lines()
            plan.write({'plan_line_ids': plan_lines})
