# -*- coding: utf-8 -*-
from openerp import fields, models
from openerp import tools


class MonitorView(models.AbstractModel):
    _name = 'monitor.view'
    _order = 'budget_method desc'

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
    amount_so_commit = fields.Float(
        string='SO Commitment',
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
    amount_consumed = fields.Float(
        string='Consumed Amount',
        readonly=True,
        help="Consumed = All Commitments + Actual",
    )
    amount_balance = fields.Float(
        string='Balance',
        readonly=True,
    )

    _monitor_view_template = """
        CREATE or REPLACE VIEW %s as (
            select dense_rank() OVER  -- Can't use row_number, it not persist
                (ORDER BY budget_method, charge_type, fiscalyear_id, %s) AS id,
                budget_method, charge_type, fiscalyear_id,
                %s,
                COALESCE(sum(planned_amount),0) planned_amount,
                COALESCE(sum(released_amount),0) released_amount,
                COALESCE(sum(amount_so_commit),0) amount_so_commit,
                COALESCE(sum(amount_pr_commit),0) amount_pr_commit,
                COALESCE(sum(amount_po_commit),0) amount_po_commit,
                COALESCE(sum(amount_exp_commit),0) amount_exp_commit,
                COALESCE(sum(amount_actual),0) amount_actual,
                COALESCE(sum(amount_so_commit),0) + COALESCE(sum(amount_pr_commit),0) + 
                COALESCE(sum(amount_po_commit),0) + COALESCE(sum(amount_exp_commit),0) + 
                COALESCE(sum(amount_actual),0) as amount_consumed,
                COALESCE(sum(released_amount),0) - COALESCE(sum(amount_consumed),0) as amount_balance
            from budget_monitor_report
            where %s
            group by budget_method, charge_type, fiscalyear_id, %s
        )
    """
    #sum(amount_so_commit) + sum(amount_actual) as amount_consumed,
    #sum(amount_balance) amount_balance 
    #COALESCE(sum(amount_so_commit),0)       
    def _create_monitor_view(self, cr, field):
        conds = [x.strip() + ' is not null' for x in field.split(',')]
        where = ' and '.join(conds)
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_template %
            (self._table, field, field, where, field))


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
