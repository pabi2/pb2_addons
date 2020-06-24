# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools


class ISSIBudgetSummaryView(models.Model):
    _name = 'issi.budget.summary.view'
    _auto = False
    _description = 'ISSI Budget Summary View'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT rpt.fiscalyear_id,
                rpt.chart_view,
                rpt.project_id,
                rpt.section_id,
                rpt.invest_asset_id,
                rpt.invest_construction_id,
                rpt.invest_construction_phase_id,
                rpt.personnel_costcenter_id,
                sum(rpt.amount_pr_commit) AS sum_pr,
                sum(rpt.amount_po_commit) AS sum_po,
                sum(rpt.amount_actual) AS sum_actual,
                sum(rpt.released_amount) AS release,
                sum(rpt.amount_exp_commit) AS sum_ex,
                sum(rpt.planned_amount) AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue,
                0 AS sum_revenue_internal,
                0 AS plan_revenue_internal,
                0 AS sum_ex_internal,
                false AS old_data,
                rpt.period_id,
                rpt.section_program_id,
                sum(rpt.amount_so_commit) AS sum_so
               FROM issi_budget_query_view rpt
              WHERE (((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'expense'::text))
              GROUP BY rpt.period_id, rpt.section_program_id, rpt.fiscalyear_id, rpt.chart_view, rpt.project_id, rpt.section_id, rpt.invest_asset_id, rpt.invest_construction_id, rpt.invest_construction_phase_id, rpt.personnel_costcenter_id
            UNION
             SELECT rpt.fiscalyear_id,
                rpt.chart_view,
                rpt.project_id,
                rpt.section_id,
                rpt.invest_asset_id,
                rpt.invest_construction_id,
                rpt.invest_construction_phase_id,
                rpt.personnel_costcenter_id,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                sum(rpt.amount_actual) AS sum_overall_revenue,
                sum(rpt.planned_amount) AS plan_overall_revenue,
                0 AS sum_revenue_internal,
                0 AS plan_revenue_internal,
                0 AS sum_ex_internal,
                false AS old_data,
                rpt.period_id,
                rpt.section_program_id,
                sum(rpt.amount_so_commit) AS sum_so
               FROM issi_budget_query_view rpt
              WHERE (((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
              GROUP BY rpt.period_id, rpt.section_program_id, rpt.fiscalyear_id, rpt.chart_view, rpt.project_id, rpt.section_id, rpt.invest_asset_id, rpt.invest_construction_id, rpt.invest_construction_phase_id, rpt.personnel_costcenter_id
            UNION
             SELECT rpt.fiscalyear_id,
                rpt.chart_view,
                rpt.project_id,
                rpt.section_id,
                rpt.invest_asset_id,
                rpt.invest_construction_id,
                rpt.invest_construction_phase_id,
                rpt.personnel_costcenter_id,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                sum(rpt.amount_actual) AS sum_actual_internal,
                sum(rpt.planned_amount) AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue,
                0 AS sum_revenue_internal,
                0 AS plan_revenue_internal,
                sum(rpt.amount_exp_commit) AS sum_ex_internal,
                false AS old_data,
                rpt.period_id,
                rpt.section_program_id,
                0 AS sum_so
               FROM issi_budget_query_view rpt
              WHERE (((rpt.charge_type)::text = 'internal'::text) AND ((rpt.budget_method)::text = 'expense'::text))
              GROUP BY rpt.period_id, rpt.section_program_id, rpt.fiscalyear_id, rpt.chart_view, rpt.project_id, rpt.section_id, rpt.invest_asset_id, rpt.invest_construction_id, rpt.invest_construction_phase_id, rpt.personnel_costcenter_id
            UNION
             SELECT rpt.fiscalyear_id,
                rpt.chart_view,
                rpt.project_id,
                rpt.section_id,
                rpt.invest_asset_id,
                rpt.invest_construction_id,
                rpt.invest_construction_phase_id,
                rpt.personnel_costcenter_id,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue,
                sum(rpt.amount_actual) AS sum_revenue_internal,
                sum(rpt.planned_amount) AS plan_revenue_internal,
                0 AS sum_ex_internal,
                false AS old_data,
                rpt.period_id,
                rpt.section_program_id,
                0 AS sum_so
               FROM issi_budget_query_view rpt
              WHERE (((rpt.charge_type)::text = 'internal'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
              GROUP BY rpt.period_id, rpt.section_program_id, rpt.fiscalyear_id, rpt.chart_view, rpt.project_id, rpt.section_id, rpt.invest_asset_id, rpt.invest_construction_id, rpt.invest_construction_phase_id, rpt.personnel_costcenter_id
            UNION
             SELECT old_prj.fiscalyear_id,
                'project_base'::character varying AS chart_view,
                old_prj.project_id,
                NULL::integer AS section_id,
                NULL::integer AS invest_asset_id,
                NULL::integer AS invest_construction_id,
                NULL::integer AS invest_construction_phase_id,
                NULL::integer AS personnel_costcenter_id,
                0 AS sum_pr,
                0 AS sum_po,
                old_prj.planned_amount AS sum_actual,
                old_prj.planned_amount AS release,
                0 AS sum_ex,
                old_prj.planned_amount AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue,
                0 AS sum_revenue_internal,
                0 AS plan_revenue_internal,
                0 AS sum_ex_internal,
                true AS old_data,
                NULL::integer AS period_id,
                NULL::integer AS section_program_id,
                0 AS sum_so
               FROM (res_project_budget_summary old_prj
                 LEFT JOIN account_fiscalyear fis ON ((old_prj.fiscalyear_id = fis.id)))
              WHERE (((old_prj.budget_method)::text = 'expense'::text) AND ((fis.name)::text <= '2018'::text) AND (old_prj.planned_amount <> (0)::double precision))
            UNION
             SELECT old_prjc.fiscalyear_id,
                'invest_construction'::character varying AS chart_view,
                NULL::integer AS project_id,
                NULL::integer AS section_id,
                NULL::integer AS invest_asset_id,
                NULL::integer AS invest_construction_id,
                old_prjc.phase_id AS invest_construction_phase_id,
                NULL::integer AS personnel_costcenter_id,
                0 AS sum_pr,
                0 AS sum_po,
                old_prjc.amount_plan AS sum_actual,
                0 AS release,
                (0)::double precision AS sum_ex,
                old_prjc.amount_plan AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenue,
                0 AS plan_overall_revenue,
                0 AS sum_revenue_internal,
                0 AS plan_revenue_internal,
                0 AS sum_ex_internal,
                true AS old_data,
                NULL::integer AS period_id,
                NULL::integer AS section_program_id,
                0 AS sum_so
               FROM (issi_invest_construction_phase_summary_view old_prjc
                 LEFT JOIN account_fiscalyear fis ON ((old_prjc.fiscalyear_id = fis.id)))
              WHERE (((fis.name)::text <= '2018'::text) AND (old_prjc.amount_plan <> (0)::double precision))
            UNION
             SELECT old_prj.fiscalyear_id,
                'project_base'::character varying AS chart_view,
                old_prj.project_id,
                NULL::integer AS section_id,
                NULL::integer AS invest_asset_id,
                NULL::integer AS invest_construction_id,
                NULL::integer AS invest_construction_phase_id,
                NULL::integer AS personnel_costcenter_id,
                0 AS sum_pr,
                0 AS sum_po,
                0 AS sum_actual,
                0 AS release,
                0 AS sum_ex,
                0 AS plan_overall_external,
                0 AS sum_actual_internal,
                0 AS plan_overall_internal,
                0 AS sum_overall_revenue,
                old_prj.planned_amount AS plan_overall_revenue,
                0 AS sum_revenue_internal,
                0 AS plan_revenue_internal,
                0 AS sum_ex_internal,
                true AS old_data,
                NULL::integer AS period_id,
                NULL::integer AS section_program_id,
                0 AS sum_so
               FROM (issi_res_project_budget_summary_view old_prj
                 LEFT JOIN account_fiscalyear fis ON ((old_prj.fiscalyear_id = fis.id)))
              WHERE (((old_prj.budget_method)::text = 'revenue'::text) AND ((fis.name)::text <= '2018'::text) AND (old_prj.planned_amount <> (0)::double precision))
        )
        """ % self._table)
        
class ISSIBudgetSummaryMonitorView(models.Model):
    _name = 'issi.budget.summary.monitor.view'
    _auto = False
    _description = 'ISSI Budget Summary Monitor View'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT fis.name AS fiscal_year,
                aa.chart_view,
                aa.project_id,
                aa.section_id,
                aa.invest_asset_id,
                aa.invest_construction_id,
                aa.invest_construction_phase_id,
                aa.personnel_costcenter_id,
                COALESCE(sum(aa.sum_pr), 0.00) AS sum_pr,
                COALESCE(sum(aa.sum_po), 0.00) AS sum_po,
                COALESCE(sum(aa.sum_actual), (0.00)::double precision) AS sum_actual,
                COALESCE(sum(aa.release), (0.00)::double precision) AS release,
                COALESCE(sum(aa.sum_ex), (0.00)::double precision) AS sum_ex,
                COALESCE(sum(aa.plan_overall_external), (0.00)::double precision) AS plan_expense_external,
                COALESCE(sum(aa.sum_actual_internal), 0.00) AS sum_actual_internal,
                COALESCE(sum(aa.plan_overall_internal), (0.00)::double precision) AS plan_expense_internal,
                COALESCE(sum(aa.sum_overall_revenue), 0.00) AS sum_revenue,
                COALESCE(sum(aa.plan_overall_revenue), (0.00)::double precision) AS plan_revenue,
                COALESCE(sum(aa.sum_revenue_internal), 0.00) AS sum_revenue_internal,
                COALESCE(sum(aa.plan_revenue_internal), (0.00)::double precision) AS plan_revenue_internal,
                COALESCE(sum(aa.sum_ex_internal), 0.00) AS sum_ex_internal,
                COALESCE(sum(aa.sum_so), 0.00) AS sum_so,
                aa.fiscalyear_id
               FROM (issi_budget_summary_view aa
                 LEFT JOIN account_fiscalyear fis ON ((aa.fiscalyear_id = fis.id)))
              GROUP BY fis.name, aa.chart_view, aa.project_id, aa.section_id, aa.invest_asset_id, aa.invest_construction_id, aa.invest_construction_phase_id, aa.personnel_costcenter_id, aa.fiscalyear_id
        )
        """ % self._table)
        
class ISSIBudgetProjectMonitorView(models.Model):
    _name = 'issi.budget.project.monitor.view'
    _auto = False
    _description = 'ISSI Budget Project Monitor View'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT query.fiscal_year,
                project.code,
                COALESCE(project.revenue_budget, (0)::double precision) AS revenue_budget,
                project.overall_revenue_plan AS plan_overall_revenue,
                project.proposal_overall_budget AS plan_proposal_overall_expense,
                project.overall_expense_budget AS plan_overall_expense,
                project.overall_expense_budget_internal AS plan_overall_expense_internal,
                    CASE
                        WHEN (project.active IS TRUE) THEN query.release
                        ELSE COALESCE(( SELECT b.released_amount
                           FROM res_project_budget_summary b
                          WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
                    END AS release,
                query.sum_pr,
                query.sum_po,
                query.sum_ex,
                    CASE
                        WHEN (query.plan_expense_external = (0)::double precision) THEN COALESCE(( SELECT b.planned_amount
                           FROM res_project_budget_summary b
                          WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
                        ELSE query.plan_expense_external
                    END AS plan_expense_external,
                query.sum_actual_external,
                query.plan_expense_internal,
                query.sum_actual_internal,
                    CASE
                        WHEN (query.plan_revenue_external = (0)::double precision) THEN COALESCE(( SELECT b.planned_amount
                           FROM res_project_budget_summary b
                          WHERE (((b.budget_method)::text = 'revenue'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
                        ELSE query.plan_revenue_external
                    END AS plan_revenue_external,
                query.sum_revenue_external,
                query.plan_revenue_internal,
                query.sum_revenue_internal,
                false AS old_data,
                query.sum_ex_internal,
                query.fiscalyear_id,
                query.project_id
               FROM (( SELECT fis.name AS fiscal_year,
                        prj.id AS project_id,
                        COALESCE(sum(src.release), (0)::double precision) AS release,
                        COALESCE(sum(src.sum_pr), (0)::numeric) AS sum_pr,
                        COALESCE(sum(src.sum_po), (0)::numeric) AS sum_po,
                        COALESCE(sum(src.sum_ex), (0)::numeric) AS sum_ex,
                        COALESCE(sum(src.plan_overall_external), (0)::double precision) AS plan_expense_external,
                        COALESCE(sum(src.sum_actual), (0)::numeric) AS sum_actual_external,
                        COALESCE(sum(src.plan_overall_internal), (0)::double precision) AS plan_expense_internal,
                        COALESCE(sum(src.sum_actual_internal), (0)::numeric) AS sum_actual_internal,
                        COALESCE(sum(src.plan_overall_revenue), (0)::double precision) AS plan_revenue_external,
                        COALESCE(sum(src.sum_overall_revenue), (0)::numeric) AS sum_revenue_external,
                        COALESCE(sum(src.plan_revenue_internal), (0)::double precision) AS plan_revenue_internal,
                        COALESCE(sum(src.sum_revenue_internal), (0)::numeric) AS sum_revenue_internal,
                        0 AS po_invoice_plan,
                        COALESCE(sum(src.sum_ex_internal), (0)::numeric) AS sum_ex_internal,
                        src.fiscalyear_id
                       FROM ((( SELECT rpt.fiscalyear_id,
                                rpt.project_id,
                                sum(rpt.amount_pr_commit) AS sum_pr,
                                sum(rpt.amount_po_commit) AS sum_po,
                                sum(rpt.amount_actual) AS sum_actual,
                                sum(rpt.released_amount) AS release,
                                sum(rpt.amount_exp_commit) AS sum_ex,
                                sum(rpt.planned_amount) AS plan_overall_external,
                                0 AS sum_actual_internal,
                                0 AS plan_overall_internal,
                                0 AS sum_overall_revenue,
                                0 AS plan_overall_revenue,
                                0 AS sum_revenue_internal,
                                0 AS plan_revenue_internal,
                                0 AS sum_ex_internal
                               FROM issi_budget_query_view rpt
                              WHERE ((rpt.project_id IS NOT NULL) AND ((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'expense'::text))
                              GROUP BY rpt.fiscalyear_id, rpt.project_id
                            UNION
                             SELECT rpt.fiscalyear_id,
                                rpt.project_id,
                                0 AS sum_pr,
                                0 AS sum_po,
                                0 AS sum_actual,
                                0 AS release,
                                0 AS sum_ex,
                                0 AS plan_overall_external,
                                0 AS sum_actual_internal,
                                0 AS plan_overall_internal,
                                sum(rpt.amount_actual) AS sum_overall_revenue,
                                sum(rpt.planned_amount) AS plan_overall_revenue,
                                0 AS sum_revenue_internal,
                                0 AS plan_revenue_internal,
                                0 AS sum_ex_internal
                               FROM issi_budget_query_view rpt
                              WHERE ((rpt.project_id IS NOT NULL) AND ((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
                              GROUP BY rpt.fiscalyear_id, rpt.project_id
                            UNION
                             SELECT rpt.fiscalyear_id,
                                rpt.project_id,
                                0 AS sum_pr,
                                0 AS sum_po,
                                0 AS sum_actual,
                                0 AS release,
                                0 AS sum_ex,
                                0 AS plan_overall_external,
                                sum(rpt.amount_actual) AS sum_actual_internal,
                                sum(rpt.planned_amount) AS plan_overall_internal,
                                0 AS sum_overall_revenue,
                                0 AS plan_overall_revenue,
                                0 AS sum_revenue_internal,
                                0 AS plan_revenue_internal,
                                sum(rpt.amount_exp_commit) AS sum_ex_internal
                               FROM issi_budget_query_view rpt
                              WHERE ((rpt.project_id IS NOT NULL) AND ((rpt.charge_type)::text = 'internal'::text) AND ((rpt.budget_method)::text = 'expense'::text))
                              GROUP BY rpt.fiscalyear_id, rpt.project_id
                            UNION
                             SELECT rpt.fiscalyear_id,
                                rpt.project_id,
                                0 AS sum_pr,
                                0 AS sum_po,
                                0 AS sum_actual,
                                0 AS release,
                                0 AS sum_ex,
                                0 AS plan_overall_external,
                                0 AS sum_actual_internal,
                                0 AS plan_overall_internal,
                                0 AS sum_overall_revenuer,
                                0 AS plan_overall_revenue,
                                sum(rpt.amount_actual) AS sum_revenue_internal,
                                sum(rpt.planned_amount) AS plan_revenue_internal,
                                0 AS sum_ex_internal
                               FROM issi_budget_query_view rpt
                              WHERE ((rpt.project_id IS NOT NULL) AND ((rpt.charge_type)::text = 'internal'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
                              GROUP BY rpt.fiscalyear_id, rpt.project_id) src
                         JOIN account_fiscalyear fis ON ((src.fiscalyear_id = fis.id)))
                         JOIN res_project prj ON ((src.project_id = prj.id)))
                      WHERE ((fis.name)::text >= '2019'::text)
                      GROUP BY fis.name, prj.id, src.fiscalyear_id) query
                 JOIN res_project project ON ((project.id = query.project_id)))
            UNION
              SELECT query.fiscal_year,
                    project.code,
                    project.revenue_budget,
                    project.overall_revenue_plan AS plan_overall_revenue,
                    project.proposal_overall_budget AS plan_proposal_overall_expense,
                    project.overall_expense_budget AS plan_overall_expense,
                    project.overall_expense_budget_internal AS plan_overall_expense_internal,
                    sum(query.release) AS release,
                    0 AS sum_pr,
                    0 AS sum_po,
                    0 AS sum_ex,
                    sum(query.plan_expense_external) AS plan_expense_external,
                    sum(query.sum_actual_external) AS sum_actual_external,
                    0 AS plan_expense_internal,
                    0 AS sum_actual_internal,
                    sum(query.plan_revenue_external) AS plan_revenue_external,
                    COALESCE(sum(query.sum_revenue_external), 0::double precision) AS sum_revenue_external,
                    0 AS plan_revenue_internal,
                    0 AS sum_revenue_internal,
                    true AS old_data,
                    0 AS sum_ex_internal,
                    query.fiscalyear_id,
                    project.id AS project_id
                   FROM ( SELECT fis.name AS fiscal_year,
                            plan.project_id,
                            plan.planned_amount AS release,
                            plan.planned_amount AS sum_actual_external,
                            plan.planned_amount AS plan_expense_external,
                            0 AS plan_revenue_external,
                            plan.fiscalyear_id,
                            0 AS sum_revenue_external
                           FROM res_project_budget_summary plan
                             LEFT JOIN account_fiscalyear fis ON plan.fiscalyear_id = fis.id
                          WHERE plan.budget_method::text = 'expense'::text AND fis.name::text <= '2018'::text AND plan.planned_amount <> 0::double precision
                        UNION
                         SELECT fis.name,
                            cc.project_id,
                            0 AS release,
                            0 AS sum_actual_external,
                            0 AS plan_expense_external,
                            COALESCE(sum(cc.planned_amount), (0)::double precision) AS plan_revenue_external,
                            cc.fiscalyear_id,
                            COALESCE(sum(cc.actual_amount), (0)::double precision) AS sum_revenue_external
                           FROM (( SELECT aa.fiscalyear_id,
                                    aa.project_id,
                                    aa.planned_amount,
                                    0 AS actual_amount
                                   FROM res_project_budget_summary aa
                                  WHERE (((aa.budget_method)::text = 'revenue'::text) AND (aa.planned_amount <> (0)::double precision))
                                UNION
                                 SELECT bb.fiscalyear_id,
                                    bb.project_id,
                                    0 AS planned_amount,
                                    sum(bb.actual_amount) AS actual_amount
                                   FROM res_project_revenue_actual bb
                                  GROUP BY bb.fiscalyear_id, bb.project_id) cc
                             LEFT JOIN account_fiscalyear fis ON ((cc.fiscalyear_id = fis.id)))
                          WHERE ((fis.name)::text <= '2018'::text)
                          GROUP BY fis.name, cc.fiscalyear_id, cc.project_id) query
                     LEFT JOIN res_project project ON query.project_id = project.id
                  GROUP BY query.fiscal_year, query.fiscalyear_id, project.code, project.id
        )
        """ % self._table)
        
class ETLISSIBudgetProjectQuery(models.Model):
    _name = 'etl.issi.budget_project.query'
    _auto = False
    _description = 'ETL ISSI Budget Project Query'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT COALESCE(( SELECT bb.fiscal_year
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), fis.name) AS fiscal_year,
                COALESCE(( SELECT bb.code
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), prj.code) AS code,
                COALESCE(prj.revenue_budget, (0)::double precision) AS revenue_budget,
                prj.overall_revenue_plan AS plan_overall_revenue,
                prj.proposal_overall_budget AS plan_proposal_overall_expense,
                prj.overall_expense_budget AS plan_overall_expense,
                prj.overall_expense_budget_internal AS plan_overall_expense_internal,
                COALESCE(( SELECT bb.release
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision) AS release,
                COALESCE(( SELECT bb.sum_pr
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_pr,
                COALESCE(( SELECT bb.sum_po
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_po,
                COALESCE(( SELECT bb.sum_ex
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_ex,
                COALESCE(( SELECT bb.plan_expense_external
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), COALESCE(( SELECT pp.plan_expense_external
                       FROM issi_budget_project_plan_view pp
                      WHERE ((yy.project_id = pp.project_id) AND (yy.fiscalyear_id = pp.fiscalyear_id))), (0)::double precision)) AS plan_expense_external,
                COALESCE(( SELECT bb.sum_actual_external
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision) AS sum_actual_external,
                COALESCE(( SELECT bb.plan_expense_internal
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision) AS plan_expense_internal,
                COALESCE(( SELECT bb.sum_actual_internal
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_actual_internal,
                COALESCE(( SELECT bb.plan_revenue_external
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), COALESCE(( SELECT pp.plan_revenue_external
                       FROM issi_budget_project_plan_view pp
                      WHERE ((yy.project_id = pp.project_id) AND (yy.fiscalyear_id = pp.fiscalyear_id))), (0)::double precision)) AS plan_revenue_external,
                COALESCE(( SELECT bb.sum_revenue_external
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_revenue_external,
                COALESCE(( SELECT bb.plan_revenue_internal
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision) AS plan_revenue_internal,
                COALESCE(( SELECT bb.sum_revenue_internal
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_revenue_internal,
                COALESCE(( SELECT bb.old_data
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), yy.old_data) AS old_data,
                COALESCE(( SELECT bb.sum_ex_internal
                       FROM issi_budget_project_monitor_view bb
                      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::numeric) AS sum_ex_internal,
                yy.fiscalyear_id,
                yy.project_id
               FROM ((( SELECT DISTINCT mm.project_id,
                        mm.fiscalyear_id,
                        mm.old_data
                       FROM issi_budget_project_monitor_view mm
                    UNION
                     SELECT DISTINCT pp.project_id,
                        pp.fiscalyear_id,
                        pp.old_data
                       FROM issi_budget_project_plan_view pp) yy
                 RIGHT JOIN account_fiscalyear fis ON ((yy.fiscalyear_id = fis.id)))
                 RIGHT JOIN res_project prj ON ((yy.project_id = prj.id)))
        )
        """ % self._table)

class ETLISSIBudgetProjectCQuery(models.Model):
    _name = 'etl.issi.budget_project.c.query'
    _auto = False
    _description = 'ETL ISSI Budget Project C Query'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT COALESCE(aa.fiscal_year, '2019'::character varying) AS fiscal_year,
                aa.chart_view,
                aa.project_id,
                aa.section_id,
                aa.invest_asset_id,
                aa.invest_construction_id,
                aa.invest_construction_phase_id,
                aa.personnel_costcenter_id,
                aa.fiscalyear_id,
                COALESCE(aa.release, (0.00)::double precision) AS plan_fiscal_external,
                COALESCE(aa.release, (0.00)::double precision) AS release_fiscal,
                0.00 AS unrelease_plan_fiscal,
                COALESCE(aa.sum_pr, 0.00) AS pr_fiscal,
                COALESCE(aa.sum_po, 0.00) AS po_fiscal,
                COALESCE(aa.sum_ex, (0.00)::double precision) AS ex_fiscal,
                aa.plan_expense_external,
                COALESCE((((aa.sum_pr + aa.sum_po))::double precision + aa.sum_ex), (0.00)::double precision) AS sum_commit,
                COALESCE(aa.sum_actual, (0.00)::double precision) AS sum_actual_external,
                COALESCE((aa.release - ((((aa.sum_pr + aa.sum_po))::double precision + aa.sum_ex) + aa.sum_actual)), (0.00)::double precision) AS remain_fiscal,
                COALESCE(aa.plan_expense_internal, (0.00)::double precision) AS plan_expense_internal,
                COALESCE(aa.sum_ex_internal, 0.00) AS sum_ex_internal,
                COALESCE(aa.sum_actual_internal, 0.00) AS sum_actual_internal,
                0.00 AS plan_overall_revenue_external,
                COALESCE(aa.sum_so, 0.00) AS so_fiscal,
                0.00 AS sum_overall_revenue_external,
                0.00 AS sum_overall_revenue_internal,
                COALESCE(aa.plan_revenue, (0.00)::double precision) AS plan_fiscal_revenue_external,
                COALESCE(aa.plan_revenue_internal, (0.00)::double precision) AS plan_fiscal_revenue_internal,
                COALESCE(aa.sum_revenue, 0.00) AS fiscal_revenue_external,
                COALESCE(aa.sum_revenue_internal, 0.00) AS fiscal_revenue_internal,
                0.00 AS sum_overall_actual,
                0.00 AS sum_overall_commit,
                0.00 AS release_overall,
                0.00 AS unrelease_plan_overall,
                0.00 AS remain_plan_overall_external,
                COALESCE(( SELECT sum(b.amount_plan_init) AS sum
                       FROM res_invest_construction_phase_plan b
                      WHERE ((b.invest_construction_phase_id = aa.invest_construction_phase_id) AND (b.fiscalyear_id = aa.fiscalyear_id))
                      GROUP BY aa.fiscalyear_id), (0)::double precision) AS amount_plan_init
               FROM (issi_budget_summary_monitor_view aa
                 LEFT JOIN account_fiscalyear fis ON ((aa.fiscalyear_id = fis.id)))
              WHERE ((aa.chart_view)::text = 'invest_construction'::text)
        )
        """ % self._table)

class etl_issi_m_investment_asset(models.Model):
    _name = 'etl.issi.m.investment.asset'
    _auto = False
    _description = 'etl_issi_m_investment_asset'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS(
             SELECT a.id AS investment_asset_id,
                fis.name AS fiscal_year,
                a.code AS invest_asset_code,
                a.name AS invest_asset_name,
                a.name_common AS invest_asset_name_common,
                hr.employee_code AS requester,
                (((COALESCE(hr.title_th, ''::text) || ' '::text) || COALESCE(hr.first_name_th, ''::text)) || ' '::text) || COALESCE(hr.last_name_th, ''::text) AS requester_name,
                sec.costcenter_code,
                sec.costcenter_name_short,
                sec.costcenter_name,
                sec.section_code,
                sec.section_name,
                sec.mission_code AS mission,
                sec.org_code,
                sec.org_name_short,
                sec.org_name_short_en AS org_name,
                sec.sector_code,
                sec.sector_name,
                sec.subsector_code,
                sec.subsector_name,
                sec.division_code,
                sec.division_name,
                asecprg.code AS section_program,
                asecprg.name AS section_program_name,
                assetprg.code AS owner_program,
                assetprg.name AS owner_program_name,
                projfund.code AS fund_type_code,
                projfund.name AS fund_type_name,
                a.location AS invest_asset_location,
                a.reason_purchase,
                a.reason_purchase_text,
                a.special,
                a.price_unit,
                a.price_other,
                a.price_total,
                a.price_subtotal,
                a.amount_plan_total,
                a.active,
                ownerprg.functional_area_code AS functional_area,
                ownerprg.functional_area_name,
                ownerprg.functional_area_active,
                ownerprg.program_group_code AS program_group,
                ownerprg.program_group_name,
                ownerprg.program_group_active,
                ownerprg.code AS program_code,
                ownerprg.name AS program_name,
                ownerprg.active AS program_active,
                ( SELECT proj.code
                       FROM res_project proj
                         JOIN res_invest_asset_res_project_rel inproj ON proj.id = inproj.res_project_id AND a.id = inproj.res_invest_asset_id) AS invest_project
               FROM res_invest_asset a
                 LEFT JOIN hr_employee h ON a.request_user_id = h.id
                 LEFT JOIN issi_hr_employee_view hr ON h.id = hr.id
                 LEFT JOIN etl_issi_m_section sec ON a.owner_section_id = sec.section_id
                 LEFT JOIN res_section ressec ON sec.section_id = ressec.id
                 LEFT JOIN res_program asecprg ON ressec.section_program_id = asecprg.id
                 LEFT JOIN project_fund_type projfund ON a.fund_type_id = projfund.id
                 LEFT JOIN account_fiscalyear fis ON a.fiscalyear_id = fis.id
                 LEFT JOIN res_program assetprg ON a.owner_program_id = assetprg.id
                 LEFT JOIN issi_m_program_view ownerprg ON a.owner_program_id = ownerprg.id
                 ORDER BY a.id)""" % self._table)

class etl_issi_budget_investment_asset_query(models.Model):
    _name = 'etl.issi.budget.investment.asset.query'
    _auto = False
    _description = 'etl_issi_budget_investment_asset_query'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (
         SELECT bb.fiscal_year,
            mm.source_budget,
            mm.plan_proposal_overall_expense,
            mm.plan_overall_external,
            mm.plan_overall_expense_internal,
            0.00 AS sum_overall_actual,
            0.00 AS sum_overall_commit,
            0.00 AS release_overall,
            0.00 AS unrelease_plan_overall,
            0.00 AS remain_plan_overall_external,
            COALESCE(bb.release, 0.00::double precision) AS plan_fiscal_external,
            COALESCE(bb.release, 0.00::double precision) AS release_fiscal,
            0.00 AS unrelease_plan_fiscal,
            COALESCE(bb.sum_pr, 0.00) AS pr_fiscal,
            COALESCE(bb.sum_po, 0.00) AS po_fiscal,
            COALESCE(bb.sum_ex, 0.00::double precision) AS ex_fiscal,
            COALESCE((bb.sum_pr + bb.sum_po)::double precision + bb.sum_ex, 0.00::double precision) AS sum_commit,
            COALESCE(bb.sum_actual, 0.00::double precision) AS sum_actual_external,
            COALESCE(bb.release - ((bb.sum_pr + bb.sum_po)::double precision + bb.sum_ex + bb.sum_actual), 0.00::double precision) AS remain_fiscal,
            COALESCE(bb.plan_expense_internal, 0.00::double precision) AS plan_expense_internal,
            COALESCE(bb.sum_ex_internal, 0.00) AS sum_ex_internal,
            COALESCE(bb.sum_actual_internal, 0.00) AS sum_actual_internal,
            0.00 AS plan_overall_revenue_external,
            COALESCE(bb.sum_so, 0.00) AS so_fiscal,
            0.00 AS sum_overall_revenue_external,
            0.00 AS sum_overall_revenue_internal,
            COALESCE(bb.plan_revenue, 0.00::double precision) AS plan_fiscal_revenue_external,
            COALESCE(bb.plan_revenue_internal, 0.00::double precision) AS plan_fiscal_revenue_internal,
            COALESCE(bb.sum_revenue, 0.00) AS fiscal_revenue_external,
            COALESCE(bb.sum_revenue_internal, 0.00) AS fiscal_revenue_internal,
                CASE
                    WHEN bb.fiscal_year::text < ((( SELECT account_fiscalyear.name
                       FROM account_fiscalyear
                      WHERE now() >= account_fiscalyear.date_start AND now() <= account_fiscalyear.date_stop))::text) THEN COALESCE(bb.sum_actual, 0.00::double precision)
                    ELSE COALESCE(bb.release, 0.00::double precision)
                END AS rolling_released_amount
           FROM ( SELECT aa.fiscal_year,
                    aa.chart_view,
                    aa.project_id,
                    aa.section_id,
                    aa.invest_asset_id,
                    aa.invest_construction_id,
                    aa.invest_construction_phase_id,
                    aa.personnel_costcenter_id,
                    aa.sum_pr,
                    aa.sum_po,
                    aa.sum_actual,
                    aa.release,
                    aa.sum_ex,
                    aa.plan_expense_external,
                    aa.sum_actual_internal,
                    aa.plan_expense_internal,
                    aa.sum_revenue,
                    aa.plan_revenue,
                    aa.sum_revenue_internal,
                    aa.plan_revenue_internal,
                    aa.sum_ex_internal,
                    aa.sum_so,
                    aa.fiscalyear_id
                   FROM issi_budget_summary_monitor_view aa
                     LEFT JOIN account_fiscalyear fis ON aa.fiscalyear_id = fis.id
                  WHERE aa.chart_view::text = 'invest_asset'::text) bb
             LEFT JOIN issi_m_source_budget_view mm ON mm.invest_asset_id = bb.invest_asset_id
          WHERE mm.budget_view = 'invest_asset'::text
          ORDER BY mm.source_budget)""" % self._table)
  
