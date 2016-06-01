# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class BudgetConsumeReport(models.Model):
    _name = 'budget.consume.report'
    _auto = False

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
    doc_ref = fields.Char(
        string='Document Ref'
    )
    doc_id = fields.Reference(
        [('purchase.request', 'Purchase Request'),
         ('purchase.order', 'Purchase Order'),
         ('hr.expense.expense', 'Expense'),
         ('account.invoice', 'Invoice')],
        string='Document ID',
        readonly=True,
    )
    amount = fields.Float(
        string='Total',
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

    def _get_sql_view(self):
        sql_view = """
            select aal.id, aal.user_id, aal.date, aal.fiscalyear_id,
                aal.doc_ref, aal.doc_id,
                -- Amount
                amount as amount,
                case when aaj.budget_commit_type = 'pr_commit'
                    then aal.amount end as amount_pr_commit,
                case when aaj.budget_commit_type = 'po_commit'
                    then aal.amount end as amount_po_commit,
                case when aaj.budget_commit_type = 'exp_commit'
                    then aal.amount end as amount_exp_commit,
                case when aaj.budget_commit_type = 'actual'
                    then aal.amount end as amount_actual,
                -- Dimensions
                %s
            from account_analytic_line aal
            join account_analytic_journal aaj on aaj.id = aal.journal_id
        """ % (self._get_dimension(),)
        return sql_view

    def _get_dimension(self):
        return 'aal.product_id, aal.activity_group_id, aal.activity_id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" %
                   (self._table, self._get_sql_view(),))
