# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields
from .budget_plan_template import BudgetPlanCommon


class BudgetPlanUnit(BudgetPlanCommon, models.Model):
    _inherit = "budget.plan.unit"

    plan_revenue_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Budget Plan Lines (EXP)',
        copy=True,
        readonly=True,
        domain=[('budget_method', '=', 'revenue')],  # Have domain
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)]},
        track_visibility='onchange',
    )
    plan_expense_line_ids = fields.One2many(
        'budget.plan.unit.line',
        'plan_id',
        string='Budget Plan Lines (REV)',
        copy=True,
        readonly=True,
        domain=[('budget_method', '=', 'expense')],  # Have domain
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
    )
    planned_expense = fields.Float(
        string='Total Expense Plan',
        compute='_compute_planned_overall',
        store=True,
    )


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
        string='0',
    )
    m1 = fields.Float(
        string='1',
    )
    m2 = fields.Float(
        string='2',
    )
    m3 = fields.Float(
        string='3',
    )
    m4 = fields.Float(
        string='4',
    )
    m5 = fields.Float(
        string='5',
    )
    m6 = fields.Float(
        string='6',
    )
    m7 = fields.Float(
        string='7',
    )
    m8 = fields.Float(
        string='8',
    )
    m9 = fields.Float(
        string='9',
    )
    m10 = fields.Float(
        string='10',
    )
    m11 = fields.Float(
        string='11',
    )
    m12 = fields.Float(
        string='12',
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select min(l.id) id, plan_id, activity_group_id, t.budget_method,
            sum(m0) m0, sum(m1) m1, sum(m2) m2, sum(m3) m3, sum(m4) m4,
            sum(m5) m5, sum(m6) m6, sum(m7) m7, sum(m8) m8, sum(m9) m9,
            sum(m10) m10, sum(m11) m11, sum(m12) m12,
            sum(planned_amount) planned_amount
            from budget_plan_unit_line l
            join budget_plan_line_template t on l.template_id = t.id
            group by plan_id, activity_group_id, t.budget_method
        )""" % (self._table, ))
