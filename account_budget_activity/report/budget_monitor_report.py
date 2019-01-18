# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetMonitorReport(models.Model):
    _name = 'budget.monitor.report'
    _auto = False

    budget_commit_type = fields.Selection(
        [('so_commit', 'SO Commitment'),
         ('pr_commit', 'PR Commitment'),
         ('po_commit', 'PO Commitment'),
         ('exp_commit', 'Expense Commitment'),
         ('actual', 'Actual'),
         ],
        string='Budget Commit Type',
    )
    analytic_line_id = fields.Many2one(
        'account.analytic.line',
        string='Analytic Line',
    )
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
    #     string='Document Ref'
    # )
    # doc_id = fields.Reference(
    #     [('sale.order', 'Sales Oder'),
    #      ('purchase.request', 'Purchase Request'),
    #      ('purchase.order', 'Purchase Order'),
    #      ('hr.expense.expense', 'Expense'),
    #      ('account.invoice', 'Invoice'),
    #      ('account.budget', 'Budget Plan')],
    #     string='Document ID',
    #     readonly=True,
    # )
    planned_amount = fields.Float(
        string='Planned Amount',
    )
    released_amount = fields.Float(
        string='Released Amount',
    )
    amount_so_commit = fields.Float(
        string='SO Commitment',
    )
    amount_pr_commit = fields.Float(
        string='PR Commitment',
    )
    amount_po_commit = fields.Float(
        string='PO Commitment',
    )
    amount_exp_commit = fields.Float(
        string='Expense Commitment',
    )
    amount_actual = fields.Float(
        string='Actual',
    )
    amount_consumed = fields.Float(
        string='Consumed',
    )
    amount_balance = fields.Float(
        string='Balance',
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
        string='Product'
    )
    product_activity_id = fields.Many2one(
        'product.activity',
        string='Product/Activity'
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
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
            select a.id,
            analytic_line_id, budget_commit_type,
            budget_method, user_id, charge_type, fiscalyear_id,
            -----> doc_ref, doc_id,
            planned_amount, released_amount, amount_so_commit,
            amount_pr_commit, amount_po_commit, amount_exp_commit,
            amount_actual, amount_consumed, amount_balance,
            coalesce(pa1.id, pa2.id) as product_activity_id,
            %s
            from
            (select id, null as analytic_line_id, null as budget_commit_type,
            budget_method, user_id, charge_type, fiscalyear_id,
            ------> doc_ref, 'account.budget,' || budget_id as doc_id,
            planned_amount, released_amount,
            0.0 as amount_so_commit, 0.0 as amount_pr_commit,
            0.0 as amount_po_commit, 0.0 as amount_exp_commit,
            0.0 as amount_actual, 0.0 as amount_consumed,
            released_amount as amount_balance,
            -- Dimensions
            %s
            from budget_plan_report
            where state in ('done')
            UNION ALL
            select id, analytic_line_id, budget_commit_type, budget_method,
            user_id, charge_type, fiscalyear_id,
            ------> doc_ref, doc_id,
            0.0 as planned_amount, 0.0 as released_amount,
            amount_so_commit, amount_pr_commit,
            amount_po_commit, amount_exp_commit,
            amount_actual, amount_consumed,
            case when budget_method = 'expense'
                then -amount else amount end as amount_balance,
            -- Dimensions
            %s
            from budget_consume_report) a
            -- Join for product.activity
            left outer join product_activity pa1
            on pa1.temp_activity_id = a.activity_id
            left outer join product_activity pa2
            on pa2.temp_product_id = a.product_id
        """ % (self._get_dimension(),
               self._get_dimension(),
               self._get_dimension(),
               )
        return sql_view

    def _get_dimension(self):
        return """
            activity_group_id, activity_id, account_id,
            product_id, period_id, quarter
        """

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
