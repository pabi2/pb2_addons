# -*- coding: utf-8 -*-
from openerp import models, fields, tools


class BudgetSectionReport(models.Model):
    _name = 'budget.section.report'
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
    section_id = fields.Many2one(
        'res.section',
        string='Section',
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
    planned_amount = fields.Float(
        string='Budget Control',
        readnly=True,
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
        readnly=True,
    )

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW budget_section_report as (
            select row_number() over (order by bmr.fiscalyear_id,
                                               ap.date_stop,
                                               bmr.costcenter_id,
                                               bmr.chart_view) as id,
                   bmr.fiscalyear_id, ap.date_stop, bmr.costcenter_id,
                   bmr.chart_view, bmr.section_id, bmr.activity_group_id,
                   bmr.activity_id,
                   sum(bmr.planned_amount) as planned_amount,
                   sum(bmr.released_amount) as released_amount,
                   sum(bmr.amount_exp_commit) as amount_exp_commit,
                   sum(bmr.amount_pr_commit) as amount_pr_commit,
                   sum(bmr.amount_po_commit) as amount_po_commit,
                   sum(bmr.amount_actual) as amount_actual
            from budget_monitor_report bmr
            left join account_period ap on ap.id = bmr.period_id
            where bmr.section_id is not null
            group by bmr.fiscalyear_id, ap.date_stop, bmr.costcenter_id,
                     bmr.chart_view, bmr.section_id, bmr.activity_group_id,
                     bmr.activity_id)""")
