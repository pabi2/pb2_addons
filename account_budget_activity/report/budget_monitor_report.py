# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools


class BudgetMonitorReport(models.Model):
    _name = 'budget.monitor.report'
    _auto = False

    user_id = fields.Many2one(
        'res.users',
        string='User',
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
    )
    doc_ref = fields.Char(
        string='Document Ref'
    )
    doc_id = fields.Reference(
        [('purchase.order', 'Purchase Order'),
         ('account.invoice', 'Invoice'),
         ('account.budget', 'Budget Plan')],
        string='Document ID',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
    )
    amount_pr_commit = fields.Float(
        string='PR Commitment',
    )
    amount_po_commit = fields.Float(
        string='PO Commitment',
    )
    amount_actual = fields.Float(
        string='Actual',
    )
    balance = fields.Float(
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

    def _get_dimension(self):
        return 'activity_group_id, activity_id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            select row_number() over (order by doc_ref) as id, * from
            (select user_id, fiscalyear_id, doc_ref,
            'account.budget,' || budget_id as doc_id,
            planned_amount, 0.0 as amount_pr_commit, 0.0 as amount_po_commit,
            0.0 as amount_actual, planned_amount as balance,
            -- Dimensions
            %s
            from budget_plan_report
            UNION
            select user_id, fiscalyear_id, doc_ref, doc_id,
            0.0 as planned_amount, amount_pr_commit, amount_po_commit,
            amount_actual, amount as balance,
            -- Dimensions
            %s
            from budget_consume_report) a
        )""" % (self._table, self._get_dimension(), self._get_dimension()))
