# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetPlanReport(models.Model):
    _name = 'budget.plan.report'
    _auto = False

    budget_method = fields.Selection(
        [('revenue', 'Revenue'),
         ('expense', 'Expense')],
        string='Budget Method',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    doc_ref = fields.Char(
        string='Budget Document',
    )
    budget_id = fields.Many2one(
        'account.budget',
        string='Budget Document',
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
        string='Jul',
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
    released_amount = fields.Float(
        string='Released Amount',
    )
    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('confirm', 'Confirmed'),
         ('validate', 'Validated'),
         ('done', 'Done')],
        string='Status',
    )
    period_id = fields.Many2one(
        'account.period',
        string="Period",
    )
    period_amount = fields.Float(
        string="Period Amount",
    )

    def _get_sql_view(self):
        sql_view = """
            select abl.id, abl.budget_method, ab.creating_user_id as user_id,
                abl.fiscalyear_id, ab.name as doc_ref, ab.id as budget_id,
                ablps.period_id as period_id,ablps.amount as period_amount,
                -- Amount
                m1, m2, m3, m4, m5, m6, m7, m8,
                m9, m10, m11, m12, abl.planned_amount, abl.released_amount,
                abl.budget_state as state,
                -- Dimensions
                %s
            from account_budget_line_period_split ablps
            join account_budget_line abl on abl.id = ablps.budget_line_id
            join account_budget ab on ab.id = abl.budget_id
        """ % (self._get_dimension(),)
        return sql_view

    def _get_dimension(self):
        return 'abl.activity_group_id, abl.activity_id, null product_id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
