# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
from .budget_plan_template import BudgetPlanCommon
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.addons.account_budget_activity.models.account_activity \
    import ActivityCommon


class BudgetPlanUnit(BudgetPlanCommon, models.Model):
    _name = 'budget.plan.unit'
    _inherits = {'budget.plan.template': 'template_id'}
    _inherit = ['mail.thread']
    _description = "Unit Based - Budget Plan"
    _order = 'create_date desc'

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
    template_id = fields.Many2one(
        'budget.plan.template',
        required=True,
        ondelete='cascade',
    )
    cost_control_ids = fields.One2many(
        'budget.plan.unit.cost.control',
        'plan_id',
        string='Job Order',
        copy=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
    )
    plan_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Budget Plan Lines',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    plan_revenue_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Revenue Plan Lines',
        copy=True,
        readonly=True,
        domain=[('budget_method', '=', 'revenue'),
                ('cost_control_id', '=', False)],  # Have domain
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Expense Plan Lines',
        copy=True,
        readonly=True,
        domain=[('budget_method', '=', 'expense'),
                ('cost_control_id', '=', False)],  # Have domain
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
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

    @api.multi
    @api.depends('plan_line_ids',
                 'cost_control_ids',
                 'cost_control_ids.detail_ids')
    def _compute_planned_overall(self):
        for rec in self:
            amounts = \
                rec.plan_summary_revenue_line_ids.mapped('planned_amount')
            rec.planned_revenue = sum(amounts)
            amounts = \
                rec.plan_summary_expense_line_ids.mapped('planned_amount')
            rec.planned_expense = sum(amounts)
            rec.planned_overall = rec.planned_revenue - rec.planned_expense

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
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
        return super(BudgetPlanUnit, self).search(args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)

    @api.onchange('fiscalyear_id')
    def onchange_fiscalyear_id(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.one
    @api.depends('fiscalyear_id')
    def _compute_date(self):
        self.date_from = self.fiscalyear_id.date_start
        self.date_to = self.fiscalyear_id.date_stop

    @api.onchange('section_id')
    def _onchange_section_id(self):
        self.org_id = self.section_id.org_id
        self.division_id = self.section_id.division_id

    # Call inherited methods
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can not delete non-draft records!'))
            rec.plan_line_ids.mapped('template_id').unlink()
        self.mapped('template_id').unlink()
        return super(BudgetPlanUnit, self).unlink()

    @api.model
    def convert_plan_to_budget_control(self, active_id):
        head_src_model = self.env['budget.plan.unit']
        line_src_model = self.env['budget.plan.unit.line']
        context = self._context.copy()
        context.update({
            'job_order_model':
                {'plan': self.env['budget.plan.unit.cost.control'],
                 'budget': self.env['budget.unit.job.order']},
            'job_order_line_model':
                {'plan': self.env['budget.plan.unit.cost.control.line'],
                 'budget': self.env['budget.unit.job.order.line']}
        })
        return self.with_context(context).\
            _convert_plan_to_budget_control(active_id,
                                            head_src_model,
                                            line_src_model)

    @api.multi  # Only Budget manager can Approve
    def button_accept(self):
        super(BudgetPlanUnit, self).button_accept()
        # Budget Manager (dept head) and only budget in the same division
        user = self.env.user
        employee = user.partner_id.employee_id
        for rec in self:
            if user.has_group('pabi_budget_plan.group_budget_manager') and \
                    employee.section_id.division_id == rec.division_id:
                continue
            elif user.id == SUPERUSER_ID:
                continue
            else:
                raise UserError(
                    _('You can approve only budget plans in division %s.') %
                    (employee.section_id.division_id.name,))
        return True


class BudgetPlanUnitLine(ActivityCommon, models.Model):
    _name = 'budget.plan.unit.line'
    _inherits = {'budget.plan.line.template': 'template_id'}
    _description = "Unit Based - Budget Plan Line"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        employee = self.env.user.partner_id.employee_id
        if self._context.get('my_org_plans', False):
            args += [('org_id', '=', employee.section_id.org_id.id)]
        if self._context.get('my_section_plans', False):
            args += [('section_id', '=', employee.section_id.id)]
        if self._context.get('my_division_plans', False):
            args += [('division_id', '=', employee.section_id.division_id.id)]
        if self._context.get('this_year_plans', False):
            current_period = self.env['account.period'].find()
            current_fiscalyear = current_period.fiscalyear_id
            args += [('fiscalyear_id', '=', current_fiscalyear.id)]
        return super(BudgetPlanUnitLine, self).search(args, offset=offset,
                                                      limit=limit, order=order,
                                                      count=count)

    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    fk_costcontrol_id = fields.Many2one(
        'budget.plan.unit.cost.control',
        string='FK Job Order',
        ondelete='cascade',
        index=True,
    )
    template_id = fields.Many2one(
        'budget.plan.line.template',
        required=True,
        index=True,
        ondelete='cascade',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submitted'),
         ('accept', 'Approved'),
         ('cancel', 'Cancelled'),
         ('reject', 'Rejected'),
         ('approve', 'Verified'),
         ('accept_corp', 'Accepted'),
         ],
        string='Status',
        related='plan_id.state',
        store=True,
    )
    breakdown_line_id = fields.Many2one(
        'budget.plan.unit.cost.control.line',
        string='Breakdown Job Order Line ref.',
    )
    activity_unit_price = fields.Float(
        string="Unit Price",
    )
    activity_unit = fields.Float(
        string="Activity Unit",
    )
    unit = fields.Float(
        string="Unit",
    )
    total_budget = fields.Float(
        string="Total Budget",
        compute="_compute_total_budget",
    )

    @api.depends('unit',
                 'activity_unit',
                 'activity_unit_price')
    def _compute_total_budget(self):
        for line in self:
            line.total_budget =\
                line.unit * line.activity_unit * line.activity_unit_price

    @api.model
    def create(self, vals):
        res = super(BudgetPlanUnitLine, self).create(vals)
        res.write({'chart_view': res.plan_id.chart_view,
                   'fiscalyear_id': res.plan_id.fiscalyear_id.id})
        return res

    @api.multi
    def unlink(self):
        self.mapped('template_id').unlink()
        return super(BudgetPlanUnitLine, self).unlink()


class BudgetPlanUnitCostControl(models.Model):
    _name = 'budget.plan.unit.cost.control'

    plan_id = fields.Many2one(
        'budget.plan.unit',
        string='Budget Plan',
        ondelete='cascade',
        index=True,
        required=True,
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
    )
    amount_total = fields.Float(
        string='Total Amount',
        compute='_compute_amount_total',
    )
    detail_ids = fields.One2many(
        'budget.plan.unit.line',
        'fk_costcontrol_id',
        string='Job Order Detail',
    )
    plan_cost_control_line_ids = fields.One2many(
        'budget.plan.unit.cost.control.line',
        'cost_control_line_id',
        string="Job Order Lines",
        copy=False,
    )

    @api.multi
    @api.depends('detail_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = \
                sum([x.planned_amount for x in rec.plan_cost_control_line_ids])


class BudgetPlanUnitCostControlLine(models.Model):
    _name = 'budget.plan.unit.cost.control.line'

    cost_control_line_id = fields.Many2one(
        'budget.plan.unit.cost.control',
        string='Job Order Line',
        index=True,
        ondelete='cascade',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        domain="[('activity_group_ids', 'in', activity_group_id)]",
    )
    name = fields.Char(
        string='Description',
    )
    m1 = fields.Float(
        string='Oct',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m2 = fields.Float(
        string='Nov',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m3 = fields.Float(
        string='Dec',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m4 = fields.Float(
        string='Jan',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m5 = fields.Float(
        string='Feb',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m6 = fields.Float(
        string='Mar',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m7 = fields.Float(
        string='Apr',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m8 = fields.Float(
        string='May',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m9 = fields.Float(
        string='Jun',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m10 = fields.Float(
        string='Jul',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m11 = fields.Float(
        string='Aug',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    m12 = fields.Float(
        string='Sep',
        required=False,
        digits_compute=dp.get_precision('Account'),
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        compute='_compute_planned_amount',
        digits_compute=dp.get_precision('Account'),
        store=True,
    )
    activity_unit_price = fields.Float(
        string="Unit Price",
    )
    activity_unit = fields.Float(
        string="Activity Unit",
    )
    unit = fields.Float(
        string="Unit",
    )
    total_budget = fields.Float(
        string="Total Budget",
        compute="_compute_total_budget",
    )

    @api.depends('unit',
                 'activity_unit',
                 'activity_unit_price')
    def _compute_total_budget(self):
        for line in self:
            line.total_budget =\
                line.unit * line.activity_unit * line.activity_unit_price

    @api.multi
    def write(self, vals):
        for record in self:
            line_exist = self.env['budget.plan.unit.line'].\
                search([('breakdown_line_id', '=', record.id)])
            if line_exist:
                line_exist.write(vals)
        return super(BudgetPlanUnitCostControlLine, self).write(vals)

    @api.multi
    @api.depends('m1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12',)
    def _compute_planned_amount(self):
        for rec in self:
            planned_amount = sum([rec.m1, rec.m2, rec.m3, rec.m4,
                                  rec.m5, rec.m6, rec.m7, rec.m8,
                                  rec.m9, rec.m10, rec.m11, rec.m12
                                  ])
            rec.planned_amount = planned_amount  # from last year


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
            select min(l.id) id, plan_id, activity_group_id, t.budget_method,
            sum(m1) m1, sum(m2) m2, sum(m3) m3, sum(m4) m4,
            sum(m5) m5, sum(m6) m6, sum(m7) m7, sum(m8) m8, sum(m9) m9,
            sum(m10) m10, sum(m11) m11, sum(m12) m12,
            sum(planned_amount) planned_amount
            from budget_plan_unit_line l
            join budget_plan_line_template t on l.template_id = t.id
            group by plan_id, activity_group_id, t.budget_method
        )""" % (self._table, ))
