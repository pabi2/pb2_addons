# -*- coding: utf-8 -*-
from openerp import fields, api
from openerp.addons.pabi_chartfield.models.chartfield import ChartField


class BPCommon(object):
    """ Budget Plan Header, no Chartfield here """

    # This is the most detailed stats for any budget plan structure.
    # We make it common, but not necessary to use all of them
    _STATE = [('draft', 'Draft'),
              ('submit', 'Submitted'),  # draft
              ('approve', 'Approved'),  # submit
              ('cancel', 'Cancelled'),  # draft,submit
              ('reject', 'Rejected'),   # submit,approve
              ('verify', 'Verified'),   # approve
              ('accept', 'Accepted'),   # verify
              # Accepted by Cooperate
              ]

    name = fields.Char(
        string='Number',
        required=True,
        default="/",
        copy=False,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
    )
    date = fields.Date(
        string='Date',
        copy=False,
        default=lambda self: fields.Date.context_today(self),
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        required=True,
        default=lambda self: self.env['account.period'].find().fiscalyear_id,
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
    )
    planned_expense = fields.Float(
        string='Total Expense Plan',
        compute='_compute_planned_overall',
        store=True,
        help="All Expense",
    )
    planned_overall = fields.Float(
        string='Total Planned',
        compute='_compute_planned_overall',
        store=True,
        help="All Revenue - All Expense",
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
        self.state = 'draft'

    @api.multi
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def action_approve(self):
        self.state = 'approve'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_reject(self):
        self.state = 'reject'

    @api.multi
    def action_verify(self):
        self.state = 'verify'

    @api.multi
    def action_accept(self):
        self.state = 'accept'


class BPLCommon(ChartField):

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
