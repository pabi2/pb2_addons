# -*- coding: utf-8 -*-
from openerp import fields, api
from openerp.addons.pabi_chartfield.models.chartfield import ChartField

# This is the most detailed stats for any budget plan structure.
# We make it common, but not necessary to use all of them
_STATE = [('draft', 'Draft'),
          ('submit', 'Submitted'),  # draft
          ('approve', 'Approved'),  # submit
          ('cancel', 'Cancelled'),  # draft,submit
          ('reject', 'Rejected'),   # submit,approve
          ('verify', 'Verified'),   # approve
          ('accept', 'Accepted'),   # verify
          ('done', 'Done'),   # verify
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
        default='draft',
        index=True,
        required=True,
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )

    @api.model
    def _get_doc_number(self, fiscalyear_id, model, res_id):
        _prefix = 'PLAN'
        fiscal = self.env['account.fiscalyear'].browse(fiscalyear_id)
        res = self.env[model].browse(res_id)
        return '%s/%s/%s' % (_prefix, fiscal.code,
                             res.code or res.name_short or res.name)

    @api.multi
    @api.depends('plan_line_ids')
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
        self.write({'state': 'draft'})

    @api.multi
    def action_submit(self):
        self.write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_reject(self):
        self.write({'state': 'reject'})

    @api.multi
    def action_verify(self):
        self.write({'state': 'verify'})

    @api.multi
    def action_accept(self):
        self.write({'state': 'accept'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

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


class BPLCommon(ChartField, Common):

    activity_group_id = fields.Many2one(
        'account.activity.group',
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
