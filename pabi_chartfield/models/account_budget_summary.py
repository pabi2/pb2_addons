# -*- coding: utf-8 -*-
from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp import models, fields, api


class BudgetUnitSummary(models.Model):
    _name = 'budget.unit.summary'
    _auto = False

    budget_id = fields.Many2one(
        'account.budget',
        string="Budget",
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
        compute='_compute_planned_amount',
        digits_compute=dp.get_precision('Account'),
    )

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

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select min(l.id) id, budget_id, activity_group_id, l.budget_method,
            sum(m1) m1, sum(m2) m2, sum(m3) m3, sum(m4) m4,
            sum(m5) m5, sum(m6) m6, sum(m7) m7, sum(m8) m8, sum(m9) m9,
            sum(m10) m10, sum(m11) m11, sum(m12) m12
            from account_budget_line l
            group by budget_id, activity_group_id, l.budget_method
        )""" % (self._table, ))


class BudgetCommitmentSummary(models.Model):
    _name = 'budget.commitment.summary'
    _auto = False

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    section_id = fields.Many2one(
        'res.section',
        string='Section',
    )
    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    # Group by fields (AG, Job Order)
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    cost_control_id = fields.Many2one(
        'cost.control',
        string='Job Order',
    )
    all_commit = fields.Float(
        string='Budget Committed Amount',
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
                select min(id) as id, fiscalyear_id, section_id, budget_method,
                    activity_group_id, cost_control_id,
                    sum(coalesce(amount_so_commit ,0.0) +
                        coalesce(amount_pr_commit, 0,0) +
                        coalesce(amount_po_commit, 0.0) +
                        coalesce(amount_exp_commit, 0.0)) as all_commit
                from budget_consume_report where section_id is not null
                group by fiscalyear_id, section_id, budget_method,
                    activity_group_id, cost_control_id
        )""" % (self._table, ))
