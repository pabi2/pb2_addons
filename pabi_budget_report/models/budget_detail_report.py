# -*- coding: utf-8 -*-
from openerp import models, fields, tools
from .budget_common_report import BudgetCommonReport


class BudgetDetailReport(models.Model, BudgetCommonReport):
    _name = 'budget.detail.report'
    _auto = False

    activity_group_id = fields.Many2one(
        'account.activity.group',
        string='Activity Group',
        readonly=True,
    )
    activity_id = fields.Many2one(
        'account.activity',
        string='Activity',
        readonly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW budget_detail_report as (
            select row_number() over (order by bmr.fiscalyear_id,
                                               ap.date_stop,
                                               bmr.costcenter_id,
                                               bmr.chart_view) as id,
                   bmr.fiscalyear_id, ap.date_stop, bmr.costcenter_id,
                   bmr.chart_view, bmr.activity_group_id, bmr.activity_id,
                   (case when bmr.section_id is not null then
                            'res.section,' || bmr.section_id
                         when bmr.project_id is not null then
                            'res.project,' || bmr.project_id
                         when bmr.invest_asset_id is not null then
                            'res.invest.asset,' || bmr.invest_asset_id
                         when bmr.invest_construction_id is not null then
                            'res.invest.construction,' ||
                            bmr.invest_construction_id
                         when bmr.personnel_costcenter_id is not null then
                            'res.personnel.costcenter,' ||
                            bmr.personnel_costcenter_id
                         else null end) as budget_id,
                   sum(bmr.planned_amount) as planned_amount,
                   sum(bmr.released_amount) as released_amount,
                   sum(bmr.amount_exp_commit) as amount_exp_commit,
                   sum(bmr.amount_pr_commit) as amount_pr_commit,
                   sum(bmr.amount_po_commit) as amount_po_commit,
                   sum(bmr.amount_actual) as amount_actual
            from budget_monitor_report bmr
            left join account_period ap on ap.id = bmr.period_id
            group by bmr.fiscalyear_id, ap.date_stop, bmr.costcenter_id,
                     bmr.chart_view, budget_id, bmr.activity_group_id,
                     bmr.activity_id)""")
