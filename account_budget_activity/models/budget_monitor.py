# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools


class MonitorView(models.AbstractModel):
    _name = 'monitor.view'

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    amount_plan = fields.Float(
        string='Planned Amount',
        readonly=True,
    )
    amount_actual = fields.Float(
        string='Actual Amount',
        readonly=True,
        compute='_amount_all',
    )
    amount_balance = fields.Float(
        string='Balance',
        readonly=True,
        compute='_amount_all',
    )

    _monitor_view_tempalte = """CREATE or REPLACE VIEW %s as (
            select ap.fiscalyear_id id,
            ap.fiscalyear_id, abl.%s,
            coalesce(sum(planned_amount), 0.0) amount_plan
        from account_period ap
            join account_budget_line abl on ap.id = abl.period_id
            join account_budget ab on ab.id = abl.budget_id
        where ab.latest_version = true and ab.state in ('validate', 'done')
        group by ap.fiscalyear_id, abl.%s)
    """

    def _create_monitor_view(self, cr, table, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_tempalte %
            (self._table, field, field))

    @api.multi
    def _amount_all(self):
        for rec in self:
            # Actual from move lines (journal = purchase, purchase_refund
            self._cr.execute("""
                select sum(debit-credit) amount_actual
                from account_move_line aml
                    join account_period ap on ap.id = aml.period_id
                where aml.%s = %s and ap.fiscalyear_id = %s
                and journal_id in
                    (select id from account_journal
                    where type in ('purchase', 'purchase_refund'));
            """ % (self._budgeting_level,
                   rec[self._budgeting_level].id, rec.fiscalyear_id.id))
            rec.amount_actual = self._cr.fetchone()[0] or 0.0
            rec.amount_balance = rec.amount_plan - rec.amount_actual


class AccountActivityGroupMonitorView(MonitorView, models.Model):
    _name = 'account.activity.group.monitor.view'
    _auto = False

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    _budgeting_level = 'activity_group_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_group_id')


class AccountActivityMonitorView(MonitorView, models.Model):
    _name = 'account.activity.monitor.view'
    _auto = False

    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )
    _budgeting_level = 'activity_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_id')
