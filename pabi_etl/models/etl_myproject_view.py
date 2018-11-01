# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools


class EtlMyProjectDetail(models.Model):
    _name = 'etl.myproject.project.detail'
    _auto = False
    _description = 'Myproject Project Detail'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
            SELECT fis.name AS fiscal_year,
                prj.code AS dim_wbs,
                "left"(pred.code::text, 2) AS period,
                act.code AS gl,
                sum(rpt.amount_actual) AS actual_amount,
                ag.code AS acctivity_group,
                fund.code AS fund,
                rpt.charge_type AS chargetype
            FROM budget_monitor_report rpt
                JOIN account_fiscalyear fis ON rpt.fiscalyear_id = fis.id
                JOIN res_project prj ON rpt.project_id = prj.id
                JOIN account_period pred ON rpt.period_id = pred.id
                JOIN account_account act ON rpt.account_id = act.id
                JOIN account_activity_group ag ON rpt.activity_group_id = ag.id
                JOIN res_fund fund ON rpt.fund_id = fund.id
            WHERE rpt.project_id IS NOT NULL AND rpt.amount_actual IS NOT NULL
            GROUP BY fis.name, prj.code, ("left"(pred.code::text, 2)),
                act.code, ag.code, fund.code, rpt.charge_type
        )
        """ % self._table)


class EtlMyProjectSummary(models.Model):
    _name = 'etl.myproject.project.summary'
    _auto = False
    _description = 'Myproject Project Summary'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT fis.name AS fiscal_year,
                prg.code AS program,
                prj.code AS dim_wbs,
                prj.name AS shdes,
                prj.date_start AS dim_stadat,
                prj.date_approve AS dim_appdat,
                prj.date_end AS dim_enddat,
                prj.state AS dim_prjstaid,
                sum(src.sum_pr) AS sum_pr,
                sum(src.sum_po) AS sum_po,
                sum(src.sum_actual) AS sum_actual,
                now() AS import_date,
                sum(src.release) AS release,
                sum(src.sum_ex) AS sum_ex,
                sum(src.plan_overall_external) AS plan_overall_external,
                sum(src.sum_actual_internal) AS sum_actual_internal,
                sum(src.plan_overall_internal) AS plan_overall_internal,
                sum(src.sum_overall_revenue) AS sum_overall_revenue,
                sum(src.plan_overall_revenue) AS plan_overall_revenue
                FROM (((( SELECT rpt.fiscalyear_id,
                rpt.project_id,
                0 AS sum_fr,
                sum(rpt.amount_pr_commit) AS sum_pr,
                sum(rpt.amount_po_commit) AS sum_po,
                sum(rpt.amount_actual) AS sum_actual,
                sum(rpt.released_amount) AS release,
                sum(rpt.amount_exp_commit) AS sum_ex,
                sum(rpt.planned_amount) AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue
            FROM budget_monitor_report rpt
            WHERE ((rpt.project_id IS NOT NULL)
                AND ((rpt.charge_type)::text = 'external'::text)
                AND ((rpt.budget_method)::text = 'expense'::text))
            GROUP BY rpt.fiscalyear_id, rpt.project_id
            UNION
            SELECT rpt.fiscalyear_id,
                rpt.project_id,
                0 AS sum_fr,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                sum(rpt.amount_actual) AS sum_overall_revenue,
                sum(rpt.planned_amount) AS plan_overall_revenue
            FROM budget_monitor_report rpt
            WHERE ((rpt.project_id IS NOT NULL)
                AND ((rpt.charge_type)::text = 'external'::text)
                AND ((rpt.budget_method)::text = 'revenue'::text))
            GROUP BY rpt.fiscalyear_id, rpt.project_id
            UNION
            SELECT rpt.fiscalyear_id,
                rpt.project_id,
                0 AS sum_fr,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                sum(rpt.amount_actual) AS sum_actual_internal,
                sum(rpt.planned_amount) AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue
            FROM budget_monitor_report rpt
            WHERE ((rpt.project_id IS NOT NULL)
                AND ((rpt.charge_type)::text = 'internal'::text)
                AND ((rpt.budget_method)::text = 'expense'::text))
            GROUP BY rpt.fiscalyear_id, rpt.project_id
            UNION
            SELECT rpt.fiscalyear_id,
                rpt.project_id,
                0 AS sum_fr,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenuer,
                0 AS plan_overall_revenue
            FROM budget_monitor_report rpt
            WHERE ((rpt.project_id IS NOT NULL)
                AND ((rpt.charge_type)::text = 'internal'::text)
                AND ((rpt.budget_method)::text = 'revenue'::text))
            GROUP BY rpt.fiscalyear_id, rpt.project_id) src
            JOIN account_fiscalyear fis ON ((src.fiscalyear_id = fis.id)))
            JOIN res_project prj ON ((src.project_id = prj.id)))
            JOIN res_program prg ON ((prj.program_id = prg.id)))
            GROUP BY fis.name, prg.code, prj.code, prj.name, prj.date_start,
                prj.date_approve, prj.date_end, prj.state
        )
        """ % self._table)
