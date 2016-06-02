# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class MonitorView(models.AbstractModel):
    _name = 'monitor.view'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    released_amount = fields.Float(
        string='Released Amount',
        readonly=True,
    )
    amount_pr_commit = fields.Float(
        string='PR Commitment',
        readonly=True,
    )
    amount_po_commit = fields.Float(
        string='PO Commitment',
        readonly=True,
    )
    amount_exp_commit = fields.Float(
        string='Expense Commitment',
        readonly=True,
    )
    amount_actual = fields.Float(
        string='Actual Amount',
        readonly=True,
    )
    amount_balance = fields.Float(
        string='Balance',
        readonly=True,
    )

    _monitor_view_tempalte = """
        CREATE or REPLACE VIEW %s as (
            select min(id) as id, fiscalyear_id,
                %s,
                sum(planned_amount) planned_amount,
                sum(released_amount) released_amount,
                sum(amount_pr_commit) amount_pr_commit,
                sum(amount_po_commit) amount_po_commit,
                sum(amount_exp_commit) amount_exp_commit,
                sum(amount_actual) amount_actual,
                sum(amount_balance) amount_balance
            from budget_monitor_report
            where %s is not null
            group by fiscalyear_id, %s
        )
    """

    def _create_monitor_view(self, cr, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_tempalte %
            (self._table, field, field, field))


class AccountActivityGroupMonitorView(models.Model):
    _name = 'account.activity.group.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'activity_group_id'

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)


class AccountActivityMonitorView(models.Model):
    _name = 'account.activity.monitor.view'
    _inherit = 'monitor.view'
    _auto = False
    _dimension = 'activity_id'

    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )

    def init(self, cr):
        self._create_monitor_view(cr, self._dimension)
