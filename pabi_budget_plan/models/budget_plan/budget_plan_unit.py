# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from .budget_plan_common import BPCommon, BPLMonthCommon
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon
# from openerp.addons.document_status_history.models.document_history import \
#     LogCommon

# We need status as extra column for sorting purposes

# _STATUS = [('1', 'Draft'),
#            ('2', 'Submitted'),
#            ('3', 'Approved'),
#            ('4', 'Cancelled'),
#            ('5', 'Rejected'),
#            ('6', 'Verified'),
#            ('7', 'Accepted'),
#            ('8', 'Done'),
#            ]
#
# _STATE_TO_STATUS = {'draft': '1',
#                     'submit': '2',
#                     'approve': '3',
#                     'cancel': '4',
#                     'reject': '5',
#                     'verify': '6',
#                     'accept': '7',
#                     'done': '8',
#                     }


class BudgetPlanUnit(BPCommon, models.Model):
    _name = 'budget.plan.unit'
    _inherit = ['mail.thread']
    _description = "Unit - Budget Plan"
    _order = 'id desc'

    # TO BE REMOVED
    @api.multi
    def show_message(self):
        raise ValidationError('Under construction!')

    # COMMON
    plan_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        readonly=True,
        states={'1_draft': [('readonly', False)],
                '2_submit': [('readonly', False)]},
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        readonly=True,
        states={'1_draft': [('readonly', False)],
                '2_submit': [('readonly', False)]},
        domain=[('budget_method', '=', 'revenue')],  # Have domain
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        readonly=True,
        states={'1_draft': [('readonly', False)],
                '2_submit': [('readonly', False)]},
        domain=[('budget_method', '=', 'expense')],  # Have domain
    )
    plan_summary_revenue_line_ids = fields.One2many(
        'budget.plan.unit.summary',
        'plan_id',
        string='Summary by Activity Group',
        domain=[('budget_method', '=', 'revenue')],
        readonly=True,
        help="Summary by Activity Group View",
    )
    plan_summary_expense_line_ids = fields.One2many(
        'budget.plan.unit.summary',
        'plan_id',
        string='Summary by Activity Group',
        domain=[('budget_method', '=', 'expense')],
        readonly=True,
        help="Summary by Activity Group View",
    )
    # Select Dimension - Section
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        required=True,
        # readonly=True,
    )
    org_id = fields.Many2one(
        'res.org',
        string='Org',
        related='section_id.org_id',
        readonly=True,
        store=True,
    )
    division_id = fields.Many2one(
        'res.division',
        string='Division',
        related='section_id.division_id',
        readonly=True,
        store=True,
    )
    # Converted to equivalant status
    # status = fields.Selection(
    #     _STATUS,
    #     string='Status',
    #     compute='_compute_status',
    #     store=True,
    #     help="This virtual field is being used to sort the status in view",
    # )
    # Data for filing import template
    master_ag_ids = fields.Many2many(
        'account.activity.group',
        sring='Activity Grups Master Data',
        compute='_compute_master_ag_ids',
    )
    master_cc_ids = fields.Many2many(
        'cost.control',
        sring='Cost Control Master Data',
        compute='_compute_master_cc_ids',
    )
    _sql_constraints = [
        ('uniq_plan', 'unique(section_id, fiscalyear_id)',
         'Duplicated budget plan for the same section is not allowed!'),
    ]

    @api.multi
    @api.depends()
    def _compute_master_ag_ids(self):
        ActivityGroup = self.env['account.activity.group']
        for rec in self:
            rec.master_ag_ids = ActivityGroup.search([]).ids

    @api.multi
    @api.depends()
    def _compute_master_cc_ids(self):
        CostControl = self.env['cost.control']
        for rec in self:
            rec.master_cc_ids = CostControl.search([]).ids

    # @api.multi
    # @api.depends('state')
    # def _compute_status(self):
    #     for rec in self:
    #         rec.status = _STATE_TO_STATUS[rec.state]

    @api.model
    def create(self, vals):
        name = self._get_doc_number(vals['fiscalyear_id'],
                                    'res.section', vals['section_id'])
        vals.update({'name': name})
        return super(BudgetPlanUnit, self).create(vals)

    @api.model
    def generate_plans(self, fiscalyear_id=None):
        if not fiscalyear_id:
            raise ValidationError(_('No fiscal year provided!'))
        # Find existing plans, and exclude them
        plans = self.search([('fiscalyear_id', '=', fiscalyear_id)])
        _ids = plans.mapped('section_id')._ids
        # Find sections
        sections = self.env['res.section'].search([('id', 'not in', _ids),
                                                   ('special', '=', False)])
        plan_ids = []
        for section in sections:
            plan = self.create({'fiscalyear_id': fiscalyear_id,
                                'section_id': section.id,
                                'user_id': False})
            plan_ids.append(plan.id)
        return plan_ids

    @api.multi
    def convert_to_budget_control(self):
        """ Create a budget control from budget plan """
        self.ensure_one()
        head_src_model = self.env['budget.plan.unit']
        line_src_model = self.env['budget.plan.unit.line']
        budget = self._convert_plan_to_budget_control(self.id,
                                                      head_src_model,
                                                      line_src_model)
        return budget

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ Add additional filter criteria """
        return super(BudgetPlanUnit, self).search(self.search_args(args),
                                                  offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)

    @api.multi
    def action_verify_to_accept(self):
        if not self.env.user.has_group('pabi_base.group_cooperate_budget'):
            raise ValidationError(_('You are not allowed to accept!'))
        if self.filtered(lambda l: l.state != '6_verify'):
            raise ValidationError(_('Only verified plan can be selected!'))
        self.action_accept()

    @api.multi
    def action_approve_to_verify(self):
        if not self.env.user.has_group('pabi_base.'
                                       'group_operating_unit_budget'):
            raise ValidationError(_('You are not allowed to verify!'))
        if self.filtered(lambda l: l.state != '3_approve'):
            raise ValidationError(_('Only approved plan can be selected!'))
        self.action_verify()

    @api.multi
    def action_submit_to_approve(self):
        if not self.env.user.has_group('pabi_base.group_budget_manager'):
            raise ValidationError(_('You are not allowed to approve!'))
        if self.filtered(lambda l: l.state != '2_submit'):
            raise ValidationError(_('Only submitted plan can be selected!'))
        self.action_approve()

    @api.multi
    def write(self, vals):
        todo = {'plan_expense_line_ids': ('Expense line',
                                          'account.activity.group',
                                          'activity_group_id'),
                'plan_revenue_line_ids': ('Revenue line',
                                          'account.activity.group',
                                          'activity_group_id')}
        PlanLine = self.env['budget.plan.unit.line']
        messages = PlanLine._change_content(vals, todo)
        for message in messages:
            self.message_post(body=message)
        return super(BudgetPlanUnit, self).write(vals)

    @api.multi
    def prepare_prev_fy_commitment(self):
        """ Prepre commitment amount from previous year from PO/EX """
        Fiscal = self.env['account.fiscalyear']
        Commit = self.env['budget.plan.unit.commit.view']
        self.mapped('plan_expense_line_ids').unlink()
        for plan in self:
            prev_fy = Fiscal.search(
                [('date_stop', '<', plan.fiscalyear_id.date_start)],
                order='date_stop desc', limit=1)
            if not prev_fy:
                return
            commits = Commit.search([
                ('section_id', '=', plan.section_id.id),
                ('fiscalyear_id', '=', prev_fy.id)])
            plan_lines = []
            for commit in commits:
                d = commit.document_id
                val = {'activity_group_id': d.activity_group_id.id,
                       'cost_control_id': d.cost_control_id.id,
                       'm0': commit.amount,
                       'description': d.name_get()[0][1],
                       }
                plan_lines.append((0, 0, val))
            plan.write({'plan_expense_line_ids': plan_lines})


class BudgetPlanUnitLine(BPLMonthCommon, ActivityCommon, models.Model):
    _name = 'budget.plan.unit.line'
    _description = "Unit - Budget Plan Line"
    _rec_name = 'activity_group_id'

    # COMMON
    chart_view = fields.Selection(
        default='unit_base',  # Unit
    )
    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    # Extra
    section_id = fields.Many2one(
        related='plan_id.section_id',
        store=True,
        readonly=True,
    )
    section_name = fields.Char(
        related='section_id.name',
        string='Section Name',
        store=True,
        readonly=True,
    )
    section_name_short = fields.Char(
        related='section_id.name_short',
        string='Section Alias',
        store=True,
        readonly=True,
    )
    section_code = fields.Char(
        related='section_id.code',
        string='Section Code',
        store=True,
        readonly=True,
    )
    mission_id = fields.Many2one(
        related='section_id.mission_id',
        string='Mission',
        store=True,
        readonly=True,
    )
    program_rpt_id = fields.Many2one(
        related='section_id.program_rpt_id',
        string='Program',
        store=True,
        readonly=True,
    )
    division_id = fields.Many2one(
        related='section_id.division_id',
        store=True,
        readonly=True,
    )
    subsector_id = fields.Many2one(
        related='section_id.subsector_id',
        store=True,
        readonly=True,
    )
    sector_id = fields.Many2one(
        related='section_id.sector_id',
        store=True,
        readonly=True,
    )
    org_id = fields.Many2one(
        related='section_id.org_id',
        store=True,
        readonly=True,
    )
    unit = fields.Float(
        string='Unit',
    )
    activity_unit_price = fields.Float(
        string='Unit Price',
    )
    activity_unit = fields.Float(
        string='Activity Unit',
    )
    total_budget = fields.Float(
        string='Total Budget',
    )
    cost_control_code = fields.Char(
        related='cost_control_id.code',
        string='Job Order Code',
        readonly=True,
        store=True,
    )
    cost_control_name = fields.Char(
        related='cost_control_id.name',
        string='Job Order Name',
        readonly=True,
        store=True,
    )
    reason = fields.Text(
        string='Reason',
    )
    # Converted to equivalant status
    # status = fields.Selection(
    #     _STATUS,
    #     related='plan_id.status',
    #     string='Status',
    #     store=True,
    #     help="This virtual field is being used to sort the status in view",
    # )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ Add additional filter criteria """
        return super(BudgetPlanUnitLine, self).search(self.search_args(args),
                                                      offset=offset,
                                                      limit=limit, order=order,
                                                      count=count)


class BudgetPlanUnitSummary(models.Model):
    _name = 'budget.plan.unit.summary'
    _auto = False
    _order = 'budget_method desc, activity_group_id'

    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    m0 = fields.Float(
        string='Prev FY',
    )
    m1 = fields.Float(
        string='Oct',
    )
    m2 = fields.Float(
        string='Nov',
    )
    m3 = fields.Float(
        string='Dec',
    )
    m4 = fields.Float(
        string='Jan',
    )
    m5 = fields.Float(
        string='Feb',
    )
    m6 = fields.Float(
        string='Mar',
    )
    m7 = fields.Float(
        string='Apr',
    )
    m8 = fields.Float(
        string='May',
    )
    m9 = fields.Float(
        string='Jun',
    )
    m10 = fields.Float(
        string='July',
    )
    m11 = fields.Float(
        string='Aug',
    )
    m12 = fields.Float(
        string='Sep',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select min(id) id, plan_id, activity_group_id, budget_method,
            sum(m0) m0, sum(m1) m1, sum(m2) m2, sum(m3) m3, sum(m4) m4,
            sum(m5) m5, sum(m6) m6, sum(m7) m7, sum(m8) m8, sum(m9) m9,
            sum(m10) m10, sum(m11) m11, sum(m12) m12,
            sum(planned_amount) planned_amount
            from budget_plan_unit_line l
            group by plan_id, activity_group_id, budget_method
        )""" % (self._table, ))


class BudgetPlanUnitCommitView(models.Model):
    _name = 'budget.plan.unit.commit.view'
    _auto = False
    _description = 'FY budget commitment for unit base'

    document_id = fields.Reference(
        [('purchase.request.line', 'PO Line'),
         ('purchase.order.line', 'PR Line'),
         ('hr.expense.line', 'EX Line'), ],
        string='Line Ref.',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        readonly=True,
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""create or replace view %s as (
            select id, fiscalyear_id, section_id, document_id, amount from (
                select max(id) id, fiscalyear_id, section_id,
                document_id, -sum(amount) amount from (
                    select id, fiscalyear_id, section_id, amount,
                    case when doctype = 'purchase_request'
                    then 'purchase.request.line,' || purchase_request_line_id
                    when doctype = 'purchase_order'
                    then 'purchase.order.line,' || purchase_line_id
                    when doctype = 'employee_expense'
                    then 'hr.expense.line,' || expense_line_id
                    else document_id
                    end
                    from account_analytic_line
                    where chart_view = 'unit_base'
                    and doctype in
                    ('purchase_request', 'purchase_order', 'employee_expense')
                    ) a
                group by fiscalyear_id, section_id, document_id
                order by fiscalyear_id, section_id, document_id) b
            where amount > 0.0
        )""" % self._table)
