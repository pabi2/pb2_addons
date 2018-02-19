# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetPlanReport(models.Model):
    _name = 'budget.plan.report'
    _auto = False

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )
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
    # doc_ref = fields.Char(
    #     string='Budget Document',
    # )
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
    account_id = fields.Many2one(
        'account.account',
        string='Account',
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
    quarter = fields.Selection(
        [('Q1', 'Q1'),
         ('Q2', 'Q2'),
         ('Q3', 'Q3'),
         ('Q4', 'Q4'),
         ],
        string="Quarter",
    )

    def _get_sql_view(self):
        sql_view = """
            select abl.id, abl.budget_method, ab.creating_user_id as user_id,
                abl.charge_type, abl.fiscalyear_id, ab.id as budget_id,
                -- Amount
                case when ablps.sequence = 1
                    then ablps.amount  end as m1,
                case when ablps.sequence = 2
                    then ablps.amount   end as m2,
                case when ablps.sequence = 3
                    then ablps.amount  end as m3,
                case when ablps.sequence = 4
                    then ablps.amount  end as m4,
                case when ablps.sequence = 5
                    then ablps.amount  end as m5,
                case when ablps.sequence = 6
                    then ablps.amount  end as m6,
                case when ablps.sequence = 7
                    then ablps.amount  end as m7,
                case when ablps.sequence = 8
                    then ablps.amount  end as m8,
                case when ablps.sequence = 9
                    then ablps.amount  end as m9,
                case when ablps.sequence = 10
                    then ablps.amount  end as m10,
                case when ablps.sequence = 11
                    then ablps.amount  end as m11,
                case when ablps.sequence = 12
                    then ablps.amount  end as m12,
                ablps.amount as planned_amount,
                case when ablps.sequence = 1  -- Release amount on m1
                    then abl.released_amount else 0.0 end as released_amount,
                abl.budget_state as state,
                -- Dimensions
                %s
            from account_budget_line_period_split ablps
            join account_budget_line abl on abl.id = ablps.budget_line_id
            join account_budget ab on ab.id = abl.budget_id
        """ % (self._get_dimension(),)
        return sql_view

    def _get_dimension(self):
        return """
            abl.activity_group_id,
            abl.activity_id,
            null account_id,
            null product_id,
            ablps.period_id as period_id,
            ablps.quarter as quarter
        """

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
