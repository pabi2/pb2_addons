# -*- coding: utf-8 -*-
from openerp import models, fields, tools


class BudgetDetailReport(models.Model):
    _name = 'budget.detail.report'
    _auto = False

    id = fields.Integer(
        string='ID',
        readonly=True,
    )
    fiscalyear_id = fields.Many2one(
        'account.fiscalyear',
        string='Fiscal Year',
        readonly=True,
    )
    date_stop = fields.Date(
        string='End of Period',
        readonly=True,
    )
    costcenter_id = fields.Many2one(
        'res.costcenter',
        string='Costcenter',
        readonly=True,
    )
    chart_view = fields.Selection(
        [('personnel', 'Personnel'),
         ('invest_asset', 'Investment Asset'),
         ('unit_base', 'Unit Based'),
         ('project_base', 'Project Based'),
         ('invest_construction', 'Investment Construction')],
        string='Budget View',
        readonly=True,
    )
    budget_id = fields.Reference(
        [('res.section', 'Section'),
         ('res.project', 'Project'),
         ('res.invest.asset', 'Investment Asset'),
         ('res.invest.construction', 'Investment Construction'),
         ('res.personnel.costcenter', 'Personnel and Welfare')],
        string='Budget Structure',
        readonly=True,
    )
    planned_amount = fields.Float(
        string='Budget Control',
        readonly=True,
    )
    released_amount = fields.Float(
        string='Budget Release',
        readonly=True,
    )
    amount_exp_commit = fields.Float(
        string='EX',
        readonly=True,
    )
    amount_pr_commit = fields.Float(
        string='PR',
        readonly=True,
    )
    amount_po_commit = fields.Float(
        string='PO',
        readonly=True,
    )
    amount_actual = fields.Float(
        string='Actual',
        readonly=True,
    )
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
