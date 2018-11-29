# -*- coding: utf-8 -*-
from openerp import tools
from openerp import fields, api, _
from openerp.exceptions import ValidationError


class PrevFYCommon(object):
    """ Super class for all budget plan previous performance views """

    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscalyear',
        readonly=True,
    )
    fund_id = fields.Many2one(
        'res.fund',
        string='Fund',
        readonly=True,
    )
    planned = fields.Float(
        string='Planned',
        readonly=True,
    )
    released = fields.Float(
        string='Released',
        readonly=True,
    )
    pr_commit = fields.Float(
        string='PR Commit',
        readonly=True,
    )
    po_commit = fields.Float(
        string='PO Commit',
        readonly=True,
    )
    exp_commit = fields.Float(
        string='EX Commit',
        readonly=True,
    )
    all_commit = fields.Float(
        string='All Commit',
        readonly=True,
    )
    actual = fields.Float(
        string='Actual',
        readonly=True,
    )
    consumed = fields.Float(
        string='Consumed',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )
    carry_forward = fields.Float(
        string='Carry Forward',
        readonly=True,
    )

    _base_prev_fy_sql = """
        select max(id) id, fiscalyear_id, fund_id, %s,
            sum(planned_amount) as planned,
            sum(released_amount) as released,
            sum(amount_pr_commit) pr_commit,
            sum(amount_po_commit) po_commit,
            sum(amount_exp_commit) exp_commit,
            sum(coalesce(amount_pr_commit, 0.0) +
                coalesce(amount_po_commit, 0.0) +
                coalesce(amount_exp_commit, 0.0)) all_commit,
            sum(amount_actual) actual,
            sum(amount_consumed) consumed,
            sum(amount_balance) balance,
            sum(coalesce(released_amount, 0.0)
                - coalesce(amount_actual, 0.0)) carry_forward
        from budget_monitor_report
        where chart_view = '%s'
            and budget_method = 'expense'
        group by fiscalyear_id, fund_id, %s
    """

    def init(self, cr):
        # Additional fields for this budget structure
        ex = ', '.join(self._ex_view_fields)
        sql = self._base_prev_fy_sql % (ex, self._chart_view, ex)
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("create or replace view %s as (%s)" % (self._table, sql))

    @api.model
    def _fill_prev_fy_performance(self, plans):
        """ Prepre actual/commit amount from previous year from PR/PO/EX """
        Fiscal = self.env['account.fiscalyear']
        plans.mapped('plan_line_ids').unlink()
        for plan in plans:
            prev_fy = Fiscal.search(
                [('date_stop', '<', plan.fiscalyear_id.date_start)],
                order='date_stop desc', limit=1)
            if not prev_fy:
                return
            ctx = {'plan_fiscalyear_id': plan.fiscalyear_id.id,
                   'prev_fiscalyear_id': prev_fy.id,
                   'lang': 'th_TH'}
            # Lookup for previous year performance only
            domain = []
            # filter: 1 = Previous Year Only, 2 = Prev and Current Planning
            if self._filter_fy not in (False, 1, 2):
                raise ValidationError(_('_filter_fy must be False, 1, 2'))
            if self._filter_fy == 1:
                domain = [('fiscalyear_id', '=', prev_fy.id)]
            elif self._filter_fy == 2:
                domain = ['|', ('fiscalyear_id', '=', prev_fy.id),
                          ('fiscalyear_id', '=', plan.fiscalyear_id.id)]
            for field in self._ex_domain_fields:
                domain.append((field, '=', plan[field].id))
            if self._ex_active_domain:
                domain += self._ex_active_domain
            # Prepare prev fy plan lines
            lines = self.search(domain)
            plan_lines = lines.with_context(ctx)._prepare_prev_fy_lines()
            plan.write({'plan_line_ids': plan_lines})
