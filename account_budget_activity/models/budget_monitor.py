# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp import tools


class MonitorView(object):
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
    amount_commit = fields.Float(
        string='Committed Amount',
        readonly=True,
        compute='_amount_all',
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
            and abl.%s is not null
        group by ap.fiscalyear_id, abl.%s)
    """

    def _create_monitor_view(self, cr, table, field):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            self._monitor_view_tempalte %
            (self._table, field, field, field))

    def _prepare_commit_amount_sql(self):
        sql = """
        select sum((price_unit / cr.rate)
                * (product_qty - invoiced_qty)) amount_commit
        from purchase_order_line pol
            join purchase_order po on pol.order_id = po.id
                and (po.date_approve is not null
                    and po.state in ('approved'))
            join account_fiscalyear af
                on (po.date_approve <= af.date_stop
                    and po.date_approve >= af.date_start)
        -- to base currency
        JOIN res_currency_rate cr ON (cr.currency_id = po.currency_id)
            AND
            cr.id IN (SELECT id
              FROM res_currency_rate cr2
              WHERE (cr2.currency_id = po.currency_id)
              AND ((po.date_approve IS NOT NULL
                      AND cr2.name <= po.date_approve)
            OR (po.date_approve IS NULL AND cr2.name <= NOW()))
              ORDER BY name DESC LIMIT 1)
        --
        where pol.%s = %s and af.id = %s
        """
        return sql

    def _prepare_actual_amount_sql(self):
        sql = """
        select sum(debit-credit) amount_actual
        from account_move_line aml
            join account_period ap on ap.id = aml.period_id
        where aml.%s = %s and ap.fiscalyear_id = %s
            and journal_id in (select id from account_journal
            where type in ('purchase', 'purchase_refund'));
        """
        return sql

    @api.multi
    def _amount_all(self):
        for rec in self:
            # Commit form purchase line (approved but not inoviced)
            self._cr.execute(self._prepare_commit_amount_sql() %
                             (self._budget_level,
                              rec[self._budget_level].id,
                              rec.fiscalyear_id.id))
            rec.amount_commit = self._cr.fetchone()[0] or 0.0
            # Actual from move lines (journal = purchase, purchase_refund)
            self._cr.execute(self._prepare_actual_amount_sql() %
                             (self._budget_level,
                              rec[self._budget_level].id,
                              rec.fiscalyear_id.id))
            rec.amount_actual = self._cr.fetchone()[0] or 0.0
            # Balance
            rec.amount_balance = (rec.amount_plan -
                                  rec.amount_commit -
                                  rec.amount_actual)


class AccountActivityGroupMonitorView(MonitorView, models.Model):
    _name = 'account.activity.group.monitor.view'
    _auto = False

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    _budget_level = 'activity_group_id'

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
    _budget_level = 'activity_id'

    def init(self, cr):
        self._create_monitor_view(cr, self._table, 'activity_id')
