# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetConsumeReport(models.Model):
    _name = 'budget.consume.report'
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
        readonly=True,
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
    date = fields.Date(
        string='Date',
    )
    # doc_ref = fields.Char(
    #     string='Document Ref'
    # )
    # doc_id = fields.Reference(
    #     [('purchase.request', 'Purchase Request'),
    #      ('purchase.order', 'Purchase Order'),
    #      ('hr.expense.expense', 'Expense'),
    #      ('account.invoice', 'Invoice')],
    #     string='Document ID',
    #     readonly=True,
    # )
    amount = fields.Float(
        string='Total',
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
    product_id = fields.Many2one(
        'product.product',
        string='Product',
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

    def _get_select_clause(self):
        sql_select = """
        select aal.id, aal.id as analytic_line_id,
            aaj.budget_commit_type,
            aal.charge_type, aal.user_id, aal.date,
            aal.monitor_fy_id fiscalyear_id,
            -------------> aal.doc_ref, aal.doc_id,
            -- Amount
            case when ag.budget_method = 'expense' then -amount
                else amount end as amount,
            -- Budget Method
            ag.budget_method,
            -- Type
            case when aaj.budget_commit_type = 'so_commit'
                then aal.amount end as amount_so_commit,
            case when aaj.budget_commit_type = 'pr_commit'
                then - aal.amount end as amount_pr_commit,
            case when aaj.budget_commit_type = 'po_commit'
                then - aal.amount end as amount_po_commit,
            case when aaj.budget_commit_type = 'exp_commit'
                then - aal.amount end as amount_exp_commit,
            case when aaj.budget_commit_type = 'actual'
                    and ag.budget_method = 'expense'
                    then - aal.amount
                when aaj.budget_commit_type = 'actual'
                    and ag.budget_method = 'revenue'
                    then aal.amount end
                as amount_actual,
            -- Dimensions
            %s
        """ % (self._get_dimension(), )
        return sql_select

    def _get_from_clause(self):
        sql_from = """
            from account_analytic_line aal
            join account_analytic_journal aaj on aaj.id = aal.journal_id
            join account_activity_group ag on ag.id = aal.activity_group_id
        """
        return sql_from

    def _get_sql_view(self):
        sql_view = """
        select *,
        coalesce(a.amount_so_commit, 0) + coalesce(a.amount_pr_commit, 0) +
        coalesce(a.amount_po_commit, 0) + coalesce(a.amount_exp_commit, 0) +
        coalesce(a.amount_actual, 0) AS amount_consumed
        from
        (%s %s) a
        """ % (self._get_select_clause(), self._get_from_clause())
        return sql_view

    def _get_dimension(self):
        return 'aal.product_id, aal.activity_group_id, aal.activity_id, ' + \
            'aal.account_id, aal.period_id, aal.quarter'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))


class BudgetCommitmentSummary(models.Model):
    _name = 'budget.commitment.summary'
    _auto = False

    charge_type = fields.Selection(
        [('internal', 'Internal'),
         ('external', 'External')],
        string='Charge Type',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
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
    all_commit = fields.Float(
        string='Budget Committed Amount',
    )

    def _get_sql_view(self):
        sql_view = """
            select * from (
                select min(id) as id, charge_type, fiscalyear_id, %s,
                    sum(coalesce(amount_so_commit ,0.0) +
                        coalesce(amount_pr_commit, 0,0) +
                        coalesce(amount_po_commit, 0.0) +
                        coalesce(amount_exp_commit, 0.0)) as all_commit
                from budget_consume_report
                group by charge_type, fiscalyear_id, %s) a
            where all_commit > 0.0
        """ % (self._get_dimension(), self._get_dimension())
        return sql_view

    def _get_dimension(self):
        return 'budget_method, activity_group_id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
