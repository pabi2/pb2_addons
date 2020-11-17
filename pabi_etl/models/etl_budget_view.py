# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools


class issi_budget_plan_view(models.Model):
    _name = 'issi.budget.plan.view'
    _auto = False
    _description = 'issi_budget_plan_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
		 SELECT abl.id,
			abl.budget_method,
			ab.creating_user_id AS user_id,
			abl.charge_type,
			abl.fiscalyear_id,
			ab.id AS budget_id,
				CASE
					WHEN (ablps.sequence = 1) THEN ablps.amount
					ELSE NULL::double precision
				END AS m1,
				CASE
					WHEN (ablps.sequence = 2) THEN ablps.amount
					ELSE NULL::double precision
				END AS m2,
				CASE
					WHEN (ablps.sequence = 3) THEN ablps.amount
					ELSE NULL::double precision
				END AS m3,
				CASE
					WHEN (ablps.sequence = 4) THEN ablps.amount
					ELSE NULL::double precision
				END AS m4,
				CASE
					WHEN (ablps.sequence = 5) THEN ablps.amount
					ELSE NULL::double precision
				END AS m5,
				CASE
					WHEN (ablps.sequence = 6) THEN ablps.amount
					ELSE NULL::double precision
				END AS m6,
				CASE
					WHEN (ablps.sequence = 7) THEN ablps.amount
					ELSE NULL::double precision
				END AS m7,
				CASE
					WHEN (ablps.sequence = 8) THEN ablps.amount
					ELSE NULL::double precision
				END AS m8,
				CASE
					WHEN (ablps.sequence = 9) THEN ablps.amount
					ELSE NULL::double precision
				END AS m9,
				CASE
					WHEN (ablps.sequence = 10) THEN ablps.amount
					ELSE NULL::double precision
				END AS m10,
				CASE
					WHEN (ablps.sequence = 11) THEN ablps.amount
					ELSE NULL::double precision
				END AS m11,
				CASE
					WHEN (ablps.sequence = 12) THEN ablps.amount
					ELSE NULL::double precision
				END AS m12,
			ablps.amount AS planned_amount,
				CASE
					WHEN (ablps.sequence = 1) THEN abl.released_amount
					ELSE (0.0)::double precision
				END AS released_amount,
			abl.budget_state AS state,
			abl.activity_group_id,
			abl.activity_id,
			NULL::integer AS account_id,
			NULL::integer AS product_id,
			ablps.period_id,
			ablps.quarter,
			abl.activity_id AS activity_rpt_id,
			abl.sector_id,
			abl.invest_construction_id,
			abl.section_program_id,
			abl.project_group_id,
			abl.program_group_id,
			abl.spa_id,
			abl.company_id,
			abl.subsector_id,
			abl.costcenter_id,
			abl.taxbranch_id,
			abl.tag_type_id,
			abl.project_id,
			abl.invest_construction_phase_id,
			abl.division_id,
			abl.cost_control_id,
			abl.section_id,
			abl.program_id,
			abl.mission_id,
			abl.tag_id,
			abl.cost_control_type_id,
			abl.personnel_costcenter_id,
			abl.functional_area_id,
			abl.org_id,
			abl.invest_asset_id,
			abl.fund_id,
			abl.chart_view,
			'account_budget'::text AS doctype,
			ab.name AS document,
			abl.description AS document_line
		   FROM ((((account_budget_line_period_split ablps
			 JOIN account_budget_line abl ON ((abl.id = ablps.budget_line_id)))
			 JOIN account_budget ab ON ((ab.id = abl.budget_id)))
			 LEFT JOIN res_section section ON ((section.id = abl.section_id)))
			 LEFT JOIN res_project project ON ((project.id = abl.project_id)))
        )
        """ % self._table)

class issi_budget_consume_view(models.Model):
    _name = 'issi.budget.consume.view'
    _auto = False
    _description = 'issi_budget_consume_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
			 SELECT a.id,
				a.analytic_line_id,
				a.budget_commit_type,
				a.charge_type,
				a.user_id,
				a.date,
				a.fiscalyear_id,
				a.amount,
				a.budget_method,
				a.amount_so_commit,
				a.amount_pr_commit,
				a.amount_po_commit,
				a.amount_exp_commit,
				a.amount_actual,
				a.product_id,
				a.activity_group_id,
				a.activity_id,
				a.account_id,
				a.period_id,
				a.quarter,
				a.activity_rpt_id,
				a.sector_id,
				a.invest_construction_id,
				a.section_program_id,
				a.project_group_id,
				a.program_group_id,
				a.spa_id,
				a.company_id,
				a.subsector_id,
				a.costcenter_id,
				a.taxbranch_id,
				a.tag_type_id,
				a.project_id,
				a.invest_construction_phase_id,
				a.division_id,
				a.cost_control_id,
				a.section_id,
				a.program_id,
				a.mission_id,
				a.tag_id,
				a.cost_control_type_id,
				a.personnel_costcenter_id,
				a.functional_area_id,
				a.org_id,
				a.invest_asset_id,
				a.fund_id,
				a.chart_view,
				a.doctype,
				a.document,
				a.document_line,
				a.purchase_request_line_id,
				a.sale_line_id,
				a.purchase_line_id,
				a.expense_line_id,
				((((COALESCE(a.amount_so_commit, (0)::numeric) + COALESCE(a.amount_pr_commit, (0)::numeric)) + COALESCE(a.amount_po_commit, (0)::numeric)) + COALESCE(a.amount_exp_commit, (0)::numeric)) + COALESCE(a.amount_actual, (0)::numeric)) AS amount_consumed,
				a.document_id
			   FROM ( SELECT aal.id,
						aal.id AS analytic_line_id,
						aaj.budget_commit_type,
						aal.charge_type,
						aal.user_id,
						aal.date,
						aal.monitor_fy_id AS fiscalyear_id,
							CASE
								WHEN ((ag.budget_method)::text = 'expense'::text) THEN (- aal.amount)
								ELSE aal.amount
							END AS amount,
						ag.budget_method,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'so_commit'::text) THEN aal.amount
								ELSE NULL::numeric
							END AS amount_so_commit,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'pr_commit'::text) THEN (- aal.amount)
								ELSE NULL::numeric
							END AS amount_pr_commit,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'po_commit'::text) THEN (- aal.amount)
								ELSE NULL::numeric
							END AS amount_po_commit,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'exp_commit'::text) THEN (- aal.amount)
								ELSE NULL::numeric
							END AS amount_exp_commit,
							CASE
								WHEN (((aaj.budget_commit_type)::text = 'actual'::text) AND ((ag.budget_method)::text = 'expense'::text)) THEN (- aal.amount)
								WHEN (((aaj.budget_commit_type)::text = 'actual'::text) AND ((ag.budget_method)::text = 'revenue'::text)) THEN aal.amount
								ELSE NULL::numeric
							END AS amount_actual,
						aal.product_id,
						aal.activity_group_id,
						aal.activity_id,
						aal.general_account_id AS account_id,
						aal.period_id,
						aal.quarter,
						aal.activity_rpt_id,
						aal.sector_id,
						aal.invest_construction_id,
						aal.section_program_id,
						aal.project_group_id,
						aal.program_group_id,
						aal.spa_id,
						aal.company_id,
						aal.subsector_id,
						aal.costcenter_id,
						aal.taxbranch_id,
						aal.tag_type_id,
						aal.project_id,
						aal.invest_construction_phase_id,
						aal.division_id,
						aal.cost_control_id,
						aal.section_id,
						aal.program_id,
						aal.mission_id,
						aal.tag_id,
						aal.cost_control_type_id,
						aal.personnel_costcenter_id,
						aal.functional_area_id,
						aal.org_id,
						aal.invest_asset_id,
						aal.fund_id,
						aal.chart_view,
						aal.doctype,
						aal.document,
						aal.document_line,
						aal.purchase_request_line_id,
						aal.sale_line_id,
						aal.purchase_line_id,
						aal.expense_line_id,
						aal.document_id
					   FROM ((((account_analytic_line aal
						 JOIN account_analytic_journal aaj ON ((aaj.id = aal.journal_id)))
						 JOIN account_activity_group ag ON ((ag.id = aal.activity_group_id)))
						 LEFT JOIN res_section section ON ((section.id = aal.section_id)))
						 LEFT JOIN res_project project ON ((project.id = aal.project_id)))) a
        )
        """ % self._table)

class issi_budget_query_view(models.Model):
    _name = 'issi.budget.query.view'
    _auto = False
    _description = 'issi_budget_query_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
		 SELECT a.analytic_line_id,
			a.budget_commit_type,
			a.budget_method,
			a.user_id,
			a.charge_type,
			a.fiscalyear_id,
			a.planned_amount,
			a.released_amount,
			a.amount_so_commit,
			a.amount_pr_commit,
			a.amount_po_commit,
			a.amount_exp_commit,
			a.amount_actual,
			a.amount_consumed,
			a.amount_balance,
			NULL::integer AS product_activity_id,
			a.activity_group_id,
			a.activity_id,
			a.account_id,
			a.product_id,
			a.period_id,
			a.quarter,
			a.activity_rpt_id,
			a.sector_id,
			a.invest_construction_id,
			a.section_program_id,
			a.project_group_id,
			a.program_group_id,
			a.spa_id,
			a.company_id,
			a.subsector_id,
			a.costcenter_id,
			a.taxbranch_id,
			a.tag_type_id,
			a.project_id,
			a.invest_construction_phase_id,
			a.division_id,
			a.cost_control_id,
			a.section_id,
			a.program_id,
			a.mission_id,
			a.tag_id,
			a.cost_control_type_id,
			a.personnel_costcenter_id,
			a.functional_area_id,
			a.org_id,
			a.invest_asset_id,
			a.fund_id,
			a.chart_view,
			a.doctype,
			a.document,
			a.document_line
		   FROM ( SELECT NULL::integer AS analytic_line_id,
					NULL::character varying AS budget_commit_type,
					issi_budget_plan_view.budget_method,
					issi_budget_plan_view.user_id,
					issi_budget_plan_view.charge_type,
					issi_budget_plan_view.fiscalyear_id,
					issi_budget_plan_view.planned_amount,
					issi_budget_plan_view.released_amount,
					0.0 AS amount_so_commit,
					0.0 AS amount_pr_commit,
					0.0 AS amount_po_commit,
					0.0 AS amount_exp_commit,
					0.0 AS amount_actual,
					0.0 AS amount_consumed,
					issi_budget_plan_view.released_amount AS amount_balance,
					issi_budget_plan_view.activity_group_id,
					issi_budget_plan_view.activity_id,
					issi_budget_plan_view.account_id,
					issi_budget_plan_view.product_id,
					issi_budget_plan_view.period_id,
					issi_budget_plan_view.quarter,
					issi_budget_plan_view.activity_rpt_id,
					issi_budget_plan_view.sector_id,
					issi_budget_plan_view.invest_construction_id,
					issi_budget_plan_view.section_program_id,
					issi_budget_plan_view.project_group_id,
					issi_budget_plan_view.program_group_id,
					issi_budget_plan_view.spa_id,
					issi_budget_plan_view.company_id,
					issi_budget_plan_view.subsector_id,
					issi_budget_plan_view.costcenter_id,
					issi_budget_plan_view.taxbranch_id,
					issi_budget_plan_view.tag_type_id,
					issi_budget_plan_view.project_id,
					issi_budget_plan_view.invest_construction_phase_id,
					issi_budget_plan_view.division_id,
					issi_budget_plan_view.cost_control_id,
					issi_budget_plan_view.section_id,
					issi_budget_plan_view.program_id,
					issi_budget_plan_view.mission_id,
					issi_budget_plan_view.tag_id,
					issi_budget_plan_view.cost_control_type_id,
					issi_budget_plan_view.personnel_costcenter_id,
					issi_budget_plan_view.functional_area_id,
					issi_budget_plan_view.org_id,
					issi_budget_plan_view.invest_asset_id,
					issi_budget_plan_view.fund_id,
					issi_budget_plan_view.chart_view,
					issi_budget_plan_view.doctype,
					issi_budget_plan_view.document,
					issi_budget_plan_view.document_line
				   FROM issi_budget_plan_view
				  WHERE ((issi_budget_plan_view.state)::text = 'done'::text)
				UNION ALL
				 SELECT issi_budget_consume_view.analytic_line_id,
					issi_budget_consume_view.budget_commit_type,
					issi_budget_consume_view.budget_method,
					issi_budget_consume_view.user_id,
					issi_budget_consume_view.charge_type,
					issi_budget_consume_view.fiscalyear_id,
					0.0 AS planned_amount,
					0.0 AS released_amount,
					issi_budget_consume_view.amount_so_commit,
					issi_budget_consume_view.amount_pr_commit,
					issi_budget_consume_view.amount_po_commit,
					issi_budget_consume_view.amount_exp_commit,
					issi_budget_consume_view.amount_actual,
					issi_budget_consume_view.amount_consumed,
						CASE
							WHEN ((issi_budget_consume_view.budget_method)::text = 'expense'::text) THEN (- issi_budget_consume_view.amount)
							ELSE issi_budget_consume_view.amount
						END AS amount_balance,
					issi_budget_consume_view.activity_group_id,
					issi_budget_consume_view.activity_id,
					issi_budget_consume_view.account_id,
					issi_budget_consume_view.product_id,
					issi_budget_consume_view.period_id,
					issi_budget_consume_view.quarter,
					issi_budget_consume_view.activity_rpt_id,
					issi_budget_consume_view.sector_id,
					issi_budget_consume_view.invest_construction_id,
					issi_budget_consume_view.section_program_id,
					issi_budget_consume_view.project_group_id,
					issi_budget_consume_view.program_group_id,
					issi_budget_consume_view.spa_id,
					issi_budget_consume_view.company_id,
					issi_budget_consume_view.subsector_id,
					issi_budget_consume_view.costcenter_id,
					issi_budget_consume_view.taxbranch_id,
					issi_budget_consume_view.tag_type_id,
					issi_budget_consume_view.project_id,
					issi_budget_consume_view.invest_construction_phase_id,
					issi_budget_consume_view.division_id,
					issi_budget_consume_view.cost_control_id,
					issi_budget_consume_view.section_id,
					issi_budget_consume_view.program_id,
					issi_budget_consume_view.mission_id,
					issi_budget_consume_view.tag_id,
					issi_budget_consume_view.cost_control_type_id,
					issi_budget_consume_view.personnel_costcenter_id,
					issi_budget_consume_view.functional_area_id,
					issi_budget_consume_view.org_id,
					issi_budget_consume_view.invest_asset_id,
					issi_budget_consume_view.fund_id,
					issi_budget_consume_view.chart_view,
					issi_budget_consume_view.doctype,
					issi_budget_consume_view.document,
					issi_budget_consume_view.document_line
				   FROM issi_budget_consume_view) a		
        )
        """ % self._table)

class etl_issi_budget_section_query(models.Model):
    _name = 'etl.issi.budget.section.query'
    _auto = False
    _description = 'etl_issi_budget_section_query'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
			 SELECT fis.name AS fiscal_year,
				sec.code AS section,
				ag.code AS ag,
				ag.name AS ag_name,
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
				now() AS import_date,
				0 AS po_invoice_plan,
				COALESCE(sum(src.sum_ex_internal), (0)::numeric) AS sum_ex_internal
			   FROM (((( SELECT rpt.fiscalyear_id,
						rpt.section_id,
						rpt.activity_group_id,
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
					  WHERE ((rpt.project_id IS NULL) AND ((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'expense'::text))
					  GROUP BY rpt.fiscalyear_id, rpt.section_id, rpt.activity_group_id
					UNION
					 SELECT rpt.fiscalyear_id,
						rpt.section_id,
						rpt.activity_group_id,
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
						sum(rpt.amount_exp_commit) AS sum_ex_internal
					   FROM issi_budget_query_view rpt
					  WHERE ((rpt.project_id IS NULL) AND ((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
					  GROUP BY rpt.fiscalyear_id, rpt.section_id, rpt.activity_group_id
					UNION
					 SELECT rpt.fiscalyear_id,
						rpt.section_id,
						rpt.activity_group_id,
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
					  WHERE ((rpt.project_id IS NULL) AND ((rpt.charge_type)::text = 'internal'::text) AND ((rpt.budget_method)::text = 'expense'::text))
					  GROUP BY rpt.fiscalyear_id, rpt.section_id, rpt.activity_group_id
					UNION
					 SELECT rpt.fiscalyear_id,
						rpt.section_id,
						rpt.activity_group_id,
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
					  WHERE ((rpt.project_id IS NULL) AND ((rpt.charge_type)::text = 'internal'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
					  GROUP BY rpt.fiscalyear_id, rpt.section_id, rpt.activity_group_id) src
				 JOIN account_fiscalyear fis ON ((src.fiscalyear_id = fis.id)))
				 LEFT JOIN res_section sec ON ((src.section_id = sec.id)))
				 LEFT JOIN account_activity_group ag ON ((src.activity_group_id = ag.id)))
			  GROUP BY fis.name, sec.id, sec.code, ag.code, ag.name
        )
        """ % self._table)

class issi_res_project_budget_summary_view(models.Model):
    _name = 'issi.res.project.budget.summary.view'
    _auto = False
    _description = 'issi_res_project_budget_summary_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
			SELECT 0 AS id,
			    aa.project_id,
			    aa.fiscalyear_id,
			    aa.budget_method,
			    sum((aa.planned_amount_internal + aa.planned_amount_external)) AS planned_amount,
			    sum((aa.released_amount_internal + aa.released_amount_external)) AS released_amount,
			    sum(aa.planned_amount_external) AS planned_amount_external,
			    sum(aa.released_amount_external) AS released_amount_external,
			    sum(aa.planned_amount_internal) AS planned_amount_internal,
			    sum(aa.released_amount_internal) AS released_amount_internal
			   FROM ( SELECT min(p.id) AS id,
				    p.project_id,
				    p.fiscalyear_id,
				    p.budget_method,
				    p.charge_type,
				    0 AS planned_amount_external,
				    0 AS released_amount_external,
					CASE
					    WHEN ((f.control_ext_charge_only = true) AND ((p.charge_type)::text = 'internal'::text)) THEN (0)::double precision
					    ELSE sum((((((((((((p.m1 + p.m2) + p.m3) + p.m4) + p.m5) + p.m6) + p.m7) + p.m8) + p.m9) + p.m10) + p.m11) + p.m12))
					END AS planned_amount_internal,
				    sum(p.released_amount) AS released_amount_internal
				   FROM (res_project_budget_plan p
				     JOIN account_fiscalyear f ON ((p.fiscalyear_id = f.id)))
				  WHERE ((p.charge_type)::text = 'internal'::text)
				  GROUP BY p.budget_method, p.project_id, p.fiscalyear_id, f.control_ext_charge_only, p.charge_type
				UNION
				 SELECT min(p.id) AS id,
				    p.project_id,
				    p.fiscalyear_id,
				    p.budget_method,
				    p.charge_type,
				    sum((((((((((((p.m1 + p.m2) + p.m3) + p.m4) + p.m5) + p.m6) + p.m7) + p.m8) + p.m9) + p.m10) + p.m11) + p.m12)) AS planned_amount_external,
				    sum(p.released_amount) AS released_amount_external,
				    0 AS planned_amount_internal,
				    0 AS released_amount_internal
				   FROM (res_project_budget_plan p
				     JOIN account_fiscalyear f ON ((p.fiscalyear_id = f.id)))
				  WHERE ((p.charge_type)::text = 'external'::text)
				  GROUP BY p.budget_method, p.project_id, p.fiscalyear_id, f.control_ext_charge_only, p.charge_type) aa
			  GROUP BY aa.project_id, aa.fiscalyear_id, aa.budget_method
        )
        """ % self._table)

class issi_invest_construction_phase_summary_view(models.Model):
    _name = 'issi.invest.construction.phase.summary.view'
    _auto = False
    _description = 'issi_invest_construction_phase_summary_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
		 SELECT min(res_invest_construction_phase_plan.id) AS id,
			res_invest_construction_phase_plan.invest_construction_phase_id AS phase_id,
			res_invest_construction_phase_plan.fiscalyear_id,
			sum(res_invest_construction_phase_plan.amount_plan) AS amount_plan,
			sum(res_invest_construction_phase_plan.amount_plan_init) AS amount_plan_init
		   FROM res_invest_construction_phase_plan
		  GROUP BY res_invest_construction_phase_plan.invest_construction_phase_id, res_invest_construction_phase_plan.fiscalyear_id
        )
        """ % self._table)

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
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
				END AS release,
			    query.sum_pr,
			    query.sum_po,
			    query.sum_ex,
				CASE
				    WHEN (query.plan_expense_external = (0)::double precision) THEN COALESCE(( SELECT b.planned_amount_external
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
				    ELSE query.plan_expense_external
				END AS plan_expense_external,
			    query.sum_actual_external,
				CASE
				    WHEN (query.plan_expense_internal = (0)::double precision) THEN COALESCE(( SELECT b.planned_amount_internal
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
				    ELSE query.plan_expense_internal
				END AS plan_expense_internal,
			    query.sum_actual_internal,
				CASE
				    WHEN (query.plan_revenue_external = (0)::double precision) THEN COALESCE(( SELECT b.planned_amount_external
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'revenue'::text) AND (b.project_id = query.project_id) AND (b.fiscalyear_id = query.fiscalyear_id))), (0)::double precision)
				    ELSE query.plan_revenue_external
				END AS plan_revenue_external,
			    query.sum_revenue_external,
			    query.plan_revenue_internal,
			    query.sum_revenue_internal,
			    false AS old_data,
			    query.sum_ex_internal,
			    query.fiscalyear_id,
			    query.project_id,
			    query.release_external,
			    query.release_internal
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
				    COALESCE(sum(src.release_external), ((0)::numeric)::double precision) AS release_external,
				    COALESCE(sum(src.release_internal), ((0)::numeric)::double precision) AS release_internal,
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
					    0 AS sum_ex_internal,
					    sum(rpt.released_amount) AS release_external,
					    0 AS release_internal
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
					    0 AS sum_ex_internal,
					    0 AS release_external,
					    0 AS release_internal
					   FROM issi_budget_query_view rpt
					  WHERE ((rpt.project_id IS NOT NULL) AND ((rpt.charge_type)::text = 'external'::text) AND ((rpt.budget_method)::text = 'revenue'::text))
					  GROUP BY rpt.fiscalyear_id, rpt.project_id
					UNION
					 SELECT rpt.fiscalyear_id,
					    rpt.project_id,
					    0 AS sum_pr,
					    0 AS sum_po,
					    0 AS sum_actual,
					    sum(rpt.released_amount) AS release,
					    0 AS sum_ex,
					    0 AS plan_overall_external,
					    sum(rpt.amount_actual) AS sum_actual_internal,
					    sum(rpt.planned_amount) AS plan_overall_internal,
					    0 AS sum_overall_revenue,
					    0 AS plan_overall_revenue,
					    0 AS sum_revenue_internal,
					    0 AS plan_revenue_internal,
					    sum(rpt.amount_exp_commit) AS sum_ex_internal,
					    0 AS release_external,
					    sum(rpt.released_amount) AS release_internal
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
					    0 AS sum_ex_internal,
					    0 AS release_external,
					    sum(rpt.released_amount) AS release_internal
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
			    COALESCE(sum(query.sum_revenue_external), (0)::double precision) AS sum_revenue_external,
			    0 AS plan_revenue_internal,
			    0 AS sum_revenue_internal,
			    true AS old_data,
			    0 AS sum_ex_internal,
			    query.fiscalyear_id,
			    project.id AS project_id,
			    sum(query.release) AS release_external,
			    0 AS release_internal
			   FROM (( SELECT fis.name AS fiscal_year,
				    plan.project_id,
				    plan.planned_amount AS release,
				    plan.planned_amount AS sum_actual_external,
				    plan.planned_amount AS plan_expense_external,
				    0 AS plan_revenue_external,
				    plan.fiscalyear_id,
				    0 AS sum_revenue_external
				   FROM (res_project_budget_summary plan
				     LEFT JOIN account_fiscalyear fis ON ((plan.fiscalyear_id = fis.id)))
				  WHERE (((plan.budget_method)::text = 'expense'::text) AND ((fis.name)::text <= '2018'::text) AND (plan.planned_amount <> (0)::double precision))
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
			     LEFT JOIN res_project project ON ((query.project_id = project.id)))
			  GROUP BY query.fiscal_year, query.fiscalyear_id, project.code, project.id
        )
        """ % self._table)

class issi_budget_project_plan_view(models.Model):
    _name = 'issi.budget.project.plan.view'
    _auto = False
    _description = 'issi_budget_project_plan_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
			 SELECT ss.project_id,
			    ss.fiscalyear_id,
			    ss.fiscal_year,
			    ss.old_data,
			    sum(ss.plan_expense_external) AS plan_expense_external,
			    sum(ss.released) AS released,
			    sum(ss.plan_revenue_external) AS plan_revenue_external,
			    sum(ss.plan_expense_internal) AS plan_expense_internal,
			    sum(ss.plan_revenue_internal) AS plan_revenue_internal
			   FROM ( SELECT aa.project_id,
				    aa.fiscalyear_id,
				    aa.planned_amount_external AS plan_expense_external,
				    aa.released_amount AS released,
				    0 AS plan_revenue_external,
				    fis.name AS fiscal_year,
					CASE
					    WHEN ((fis.name)::text <= '2018'::text) THEN true
					    ELSE false
					END AS old_data,
				    0 AS plan_expense_internal,
				    0 AS plan_revenue_internal
				   FROM (issi_res_project_budget_summary_view aa
				     LEFT JOIN account_fiscalyear fis ON ((aa.fiscalyear_id = fis.id)))
				  WHERE ((aa.budget_method)::text = 'expense'::text)
				UNION
				 SELECT bb.project_id,
				    bb.fiscalyear_id,
				    0 AS plan_expense_external,
				    0 AS released,
				    bb.planned_amount_external AS plan_revenue_external,
				    fis.name AS fiscal_year,
					CASE
					    WHEN ((fis.name)::text <= '2018'::text) THEN true
					    ELSE false
					END AS old_data,
				    0 AS plan_expense_internal,
				    0 AS plan_revenue_internal
				   FROM (issi_res_project_budget_summary_view bb
				     LEFT JOIN account_fiscalyear fis ON ((bb.fiscalyear_id = fis.id)))
				  WHERE ((bb.budget_method)::text = 'revenue'::text)
				UNION
				 SELECT p.project_id,
				    p.fiscalyear_id,
				    0 AS plan_expense_external,
				    0 AS released,
				    0 AS plan_revenue_external,
				    fis.name AS fiscal_year,
					CASE
					    WHEN ((fis.name)::text <= '2018'::text) THEN true
					    ELSE false
					END AS old_data,
				    sum((((((((((((p.m1 + p.m2) + p.m3) + p.m4) + p.m5) + p.m6) + p.m7) + p.m8) + p.m9) + p.m10) + p.m11) + p.m12)) AS plan_expense_internal,
				    0 AS plan_revenue_internal
				   FROM (res_project_budget_plan p
				     JOIN account_fiscalyear fis ON ((p.fiscalyear_id = fis.id)))
				  WHERE (((p.charge_type)::text = 'internal'::text) AND ((p.budget_method)::text = 'expense'::text))
				  GROUP BY p.project_id, p.fiscalyear_id, p.budget_method, fis.name
				UNION
				 SELECT p.project_id,
				    p.fiscalyear_id,
				    0 AS plan_expense_external,
				    0 AS released,
				    0 AS plan_revenue_external,
				    fis.name AS fiscal_year,
					CASE
					    WHEN ((fis.name)::text <= '2018'::text) THEN true
					    ELSE false
					END AS old_data,
				    0 AS plan_expense_internal,
				    sum((((((((((((p.m1 + p.m2) + p.m3) + p.m4) + p.m5) + p.m6) + p.m7) + p.m8) + p.m9) + p.m10) + p.m11) + p.m12)) AS plan_revenue_internal
				   FROM (res_project_budget_plan p
				     JOIN account_fiscalyear fis ON ((p.fiscalyear_id = fis.id)))
				  WHERE (((p.charge_type)::text = 'internal'::text) AND ((p.budget_method)::text = 'revenue'::text))
				  GROUP BY p.project_id, p.fiscalyear_id, p.budget_method, fis.name) ss
			  GROUP BY ss.project_id, ss.fiscalyear_id, ss.fiscal_year, ss.old_data
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
				CASE
				    WHEN (prj.active = false) THEN COALESCE(( SELECT b.released_amount
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = yy.project_id) AND (b.fiscalyear_id = yy.fiscalyear_id))), (0)::double precision)
				    ELSE COALESCE(( SELECT bb.release
				       FROM issi_budget_project_monitor_view bb
				      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision)
				END AS release,
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
				  WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), COALESCE(( SELECT pp.plan_expense_internal
				   FROM issi_budget_project_plan_view pp
				  WHERE ((yy.project_id = pp.project_id) AND (yy.fiscalyear_id = pp.fiscalyear_id))), (0)::double precision)) AS plan_expense_internal,
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
				  WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), ((0)::numeric)::double precision) AS sum_revenue_external,
			    COALESCE(( SELECT bb.plan_revenue_internal
				   FROM issi_budget_project_monitor_view bb
				  WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), COALESCE(( SELECT pp.plan_revenue_internal
				   FROM issi_budget_project_plan_view pp
				  WHERE ((yy.project_id = pp.project_id) AND (yy.fiscalyear_id = pp.fiscalyear_id))), (0)::double precision)) AS plan_revenue_internal,
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
			    yy.project_id,
				CASE
				    WHEN (prj.active = false) THEN COALESCE(( SELECT b.released_amount_external
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = yy.project_id) AND (b.fiscalyear_id = yy.fiscalyear_id))), (0)::double precision)
				    ELSE COALESCE(( SELECT bb.release_external
				       FROM issi_budget_project_monitor_view bb
				      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision)
				END AS released_external,
				CASE
				    WHEN (prj.active = false) THEN COALESCE(( SELECT b.released_amount_internal
				       FROM issi_res_project_budget_summary_view b
				      WHERE (((b.budget_method)::text = 'expense'::text) AND (b.project_id = yy.project_id) AND (b.fiscalyear_id = yy.fiscalyear_id))), (0)::double precision)
				    ELSE COALESCE(( SELECT bb.release_internal
				       FROM issi_budget_project_monitor_view bb
				      WHERE ((yy.project_id = bb.project_id) AND (yy.fiscalyear_id = bb.fiscalyear_id))), (0)::double precision)
				END AS released_internal
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

class issi_budget_summary_consume_view(models.Model):
    _name = 'issi.budget.summary.consume.view'
    _auto = False
    _description = 'issi_budget_summary_consume_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT a.budget_commit_type,
				a.charge_type,
				a.fiscalyear_id,
				sum(a.amount) AS amount,
				a.budget_method,
				sum(a.amount_so_commit) AS amount_so_commit,
				sum(a.amount_pr_commit) AS amount_pr_commit,
				sum(a.amount_po_commit) AS amount_po_commit,
				sum(a.amount_exp_commit) AS amount_exp_commit,
				sum(a.amount_actual) AS amount_actual,
				a.product_id,
				a.activity_group_id,
				a.activity_id,
				a.account_id,
				a.period_id,
				a.quarter,
				a.activity_rpt_id,
				a.sector_id,
				a.invest_construction_id,
				a.section_program_id,
				a.project_group_id,
				a.program_group_id,
				a.spa_id,
				a.company_id,
				a.subsector_id,
				a.costcenter_id,
				a.taxbranch_id,
				a.tag_type_id,
				a.project_id,
				a.invest_construction_phase_id,
				a.division_id,
				a.cost_control_id,
				a.section_id,
				a.program_id,
				a.mission_id,
				a.tag_id,
				a.cost_control_type_id,
				a.personnel_costcenter_id,
				a.functional_area_id,
				a.org_id,
				a.invest_asset_id,
				a.fund_id,
				a.chart_view,
				a.doctype,
				a.document,
				a.document_line,
				a.purchase_request_line_id,
				a.sale_line_id,
				a.purchase_line_id,
				a.expense_line_id,
				sum(((((COALESCE(a.amount_so_commit, (0)::numeric) + COALESCE(a.amount_pr_commit, (0)::numeric)) + COALESCE(a.amount_po_commit, (0)::numeric)) + COALESCE(a.amount_exp_commit, (0)::numeric)) + COALESCE(a.amount_actual, (0)::numeric))) AS amount_consumed,
				a.document_id,
				replace("substring"((a.document_id)::text, 0, "position"((a.document_id)::text, ','::text)), '.'::text, '_'::text) AS document_ref,
				to_number("substring"((a.document_id)::text, ("position"((a.document_id)::text, ','::text) + 1)), '999999999'::text) AS document_ref_id,
				a.move_id
			   FROM ( SELECT aal.id,
						aal.id AS analytic_line_id,
						aaj.budget_commit_type,
						aal.charge_type,
						aal.user_id,
						aal.date,
						aal.monitor_fy_id AS fiscalyear_id,
							CASE
								WHEN ((ag.budget_method)::text = 'expense'::text) THEN (- aal.amount)
								ELSE aal.amount
							END AS amount,
						ag.budget_method,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'so_commit'::text) THEN aal.amount
								ELSE NULL::numeric
							END AS amount_so_commit,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'pr_commit'::text) THEN (- aal.amount)
								ELSE NULL::numeric
							END AS amount_pr_commit,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'po_commit'::text) THEN (- aal.amount)
								ELSE NULL::numeric
							END AS amount_po_commit,
							CASE
								WHEN ((aaj.budget_commit_type)::text = 'exp_commit'::text) THEN (- aal.amount)
								ELSE NULL::numeric
							END AS amount_exp_commit,
							CASE
								WHEN (((aaj.budget_commit_type)::text = 'actual'::text) AND ((ag.budget_method)::text = 'expense'::text)) THEN (- aal.amount)
								WHEN (((aaj.budget_commit_type)::text = 'actual'::text) AND ((ag.budget_method)::text = 'revenue'::text)) THEN aal.amount
								ELSE NULL::numeric
							END AS amount_actual,
						aal.product_id,
						aal.activity_group_id,
						aal.activity_id,
						aal.general_account_id AS account_id,
						aal.period_id,
						aal.quarter,
						aal.activity_rpt_id,
						aal.sector_id,
						aal.invest_construction_id,
						aal.section_program_id,
						aal.project_group_id,
						aal.program_group_id,
						aal.spa_id,
						aal.company_id,
						aal.subsector_id,
						aal.costcenter_id,
						aal.taxbranch_id,
						aal.tag_type_id,
						aal.project_id,
						aal.invest_construction_phase_id,
						aal.division_id,
						aal.cost_control_id,
						aal.section_id,
						aal.program_id,
						aal.mission_id,
						aal.tag_id,
						aal.cost_control_type_id,
						aal.personnel_costcenter_id,
						aal.functional_area_id,
						aal.org_id,
						aal.invest_asset_id,
						aal.fund_id,
						aal.chart_view,
						aal.doctype,
						aal.document,
						aal.document_line,
						aal.purchase_request_line_id,
						aal.sale_line_id,
						aal.purchase_line_id,
						aal.expense_line_id,
						aal.document_id,
						aal.move_id
					   FROM ((((account_analytic_line aal
						 JOIN account_analytic_journal aaj ON ((aaj.id = aal.journal_id)))
						 JOIN account_activity_group ag ON ((ag.id = aal.activity_group_id)))
						 LEFT JOIN res_section section ON ((section.id = aal.section_id)))
						 LEFT JOIN res_project project ON ((project.id = aal.project_id)))) a
			  GROUP BY a.budget_commit_type, a.charge_type, a.fiscalyear_id, a.budget_method, a.product_id, a.activity_group_id, a.activity_id, a.account_id, a.period_id, a.quarter, a.activity_rpt_id, a.sector_id, a.invest_construction_id, a.section_program_id, a.project_group_id, a.program_group_id, a.spa_id, a.company_id, a.subsector_id, a.costcenter_id, a.taxbranch_id, a.tag_type_id, a.project_id, a.invest_construction_phase_id, a.division_id, a.cost_control_id, a.section_id, a.program_id, a.mission_id, a.tag_id, a.cost_control_type_id, a.personnel_costcenter_id, a.functional_area_id, a.org_id, a.invest_asset_id, a.fund_id, a.chart_view, a.doctype, a.document, a.document_line, a.purchase_request_line_id, a.sale_line_id, a.purchase_line_id, a.expense_line_id, a.document_id, a.move_id			
        )
        """ % self._table)

class issi_actual_ref_invoice_view(models.Model):
    _name = 'issi.actual.ref.invoice.view'
    _auto = False
    _description = 'issi_actual_ref_invoice_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT aa.invoice_id,
				aa.invoice_number,
				aa.invoice_description,
				aa.origin,
				aa.state AS invoice_state,
				aa.doc_date,
				aa.posting_date,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN po.name
						WHEN (aa.document_ref = 'sale_order'::text) THEN so.name
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN hr_exp.number
						ELSE ''::character varying
					END AS ref1_doc,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN po.date_order
						WHEN (aa.document_ref = 'sale_order'::text) THEN so.date_order
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN (hr_exp.date)::timestamp without time zone
						ELSE NULL::timestamp without time zone
					END AS ref1_doc_date,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN po.state
						WHEN (aa.document_ref = 'sale_order'::text) THEN so.state
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN hr_exp.state
						ELSE NULL::character varying
					END AS ref1_doc_state,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN pd.name
						ELSE ''::character varying
					END AS ref2_doc,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN pd.create_date
						ELSE NULL::timestamp without time zone
					END AS ref2_doc_date,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN pd.state
						ELSE ''::character varying
					END AS ref2_doc_state,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN pd_hrreq.employee_code
						WHEN (aa.document_ref = 'sale_order'::text) THEN ''::character varying
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrreq.employee_code
						ELSE NULL::character varying
					END AS requested_by,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN ((((COALESCE(pd_hrreq.title_th, ''::text) || ' '::text) || pd_hrreq.first_name_th) || ' '::text) || pd_hrreq.last_name_th)
						WHEN (aa.document_ref = 'sale_order'::text) THEN ''::text
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrreq.title_th, ''::text) || ' '::text) || exp_hrreq.first_name_th) || ' '::text) || exp_hrreq.last_name_th)
						ELSE NULL::text
					END AS requested_by_name,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN pd_hrapp.employee_code
						WHEN (aa.document_ref = 'sale_order'::text) THEN ''::character varying
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrapp.employee_code
						ELSE NULL::character varying
					END AS approver,
					CASE
						WHEN (aa.document_ref = 'purchase_order'::text) THEN ((((COALESCE(pd_hrapp.title_th, ''::text) || ' '::text) || pd_hrapp.first_name_th) || ' '::text) || pd_hrapp.last_name_th)
						WHEN (aa.document_ref = 'sale_order'::text) THEN ''::text
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrapp.title_th, ''::text) || ' '::text) || exp_hrapp.first_name_th) || ' '::text) || exp_hrapp.last_name_th)
						ELSE NULL::text
					END AS approver_name,
				aa.source_document,
				po.date_contract_start AS po_date_contract_start,
				po.date_contract_end AS po_date_contract_end,
				po.date_approve AS po_date_approve,
				po.contract_id,
				aa.ref_docs,
				po.order_id AS po_order_id,
				po.requisition_id,
				po.quote_id,
				po.id AS po_id
			   FROM (((((((((((( SELECT a.id AS invoice_id,
						a.number AS invoice_number,
						a.invoice_description,
						a.reference,
						a.origin,
						a.date_document AS doc_date,
						a.ref_docs,
						a.date_invoice AS posting_date,
						a.date_paid AS paid_date,
						a.partner_id,
						a.partner_code,
						a.state,
						a.expense_id,
						a.advance_expense_id,
						a.source_document_type,
						a.source_document,
						a.source_document_id,
						replace("substring"((a.source_document_id)::text, 0, "position"((a.source_document_id)::text, ','::text)), '.'::text, '_'::text) AS document_ref,
						to_number("substring"((a.source_document_id)::text, ("position"((a.source_document_id)::text, ','::text) + 1)), '999999999'::text) AS document_ref_id,
						a.amount_expense_request,
						a.amount_retention,
						a.amount_untaxed,
						a.amount_tax,
						a.amount_total
					   FROM account_invoice a) aa
				 LEFT JOIN purchase_order po ON ((aa.document_ref_id = (po.id)::numeric)))
				 LEFT JOIN purchase_requisition pd ON ((po.requisition_id = pd.id)))
				 LEFT JOIN res_users pd_requsr ON ((pd.request_uid = pd_requsr.id)))
				 LEFT JOIN issi_hr_employee_view pd_hrreq ON (((pd_requsr.login)::text = (pd_hrreq.employee_code)::text)))
				 LEFT JOIN res_users pd_appusr ON ((pd.assign_uid = pd_appusr.id)))
				 LEFT JOIN issi_hr_employee_view pd_hrapp ON (((pd_appusr.login)::text = (pd_hrapp.employee_code)::text)))
				 LEFT JOIN sale_order so ON ((aa.document_ref_id = (so.id)::numeric)))
				 LEFT JOIN hr_expense_expense hr_exp ON ((aa.document_ref_id = (hr_exp.id)::numeric)))
				 LEFT JOIN issi_hr_employee_view exp_hrreq ON ((hr_exp.employee_id = exp_hrreq.id)))
				 LEFT JOIN res_users exp_usrapp ON ((hr_exp.approver_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrapp ON (((exp_usrapp.login)::text = (exp_hrapp.employee_code)::text)))
        )
        """ % self._table)

class issi_actual_ref_stock_picking_view(models.Model):
    _name = 'issi.actual.ref.stock.picking.view'
    _auto = False
    _description = 'issi_actual_ref_stock_picking_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT a.id AS stock_picking_id,
				a.name AS stock_picking_doc,
				a.state AS stock_picking_state,
				a.origin AS stock_picking_origin,
				wa.name AS ref1_doc,
				wa.date_accept AS ref1_doc_date,
				wa.state AS ref1_doc_state,
				po.name AS ref2_doc,
				po.date_order AS ref2_doc_date,
				po.state AS ref2_doc_state,
				pd_hrreq.employee_code AS requested_by,
				((((COALESCE(pd_hrreq.title_th, ''::text) || ' '::text) || pd_hrreq.first_name_th) || ' '::text) || pd_hrreq.last_name_th) AS requested_by_name,
				pd_hrapp.employee_code AS approver,
				((((COALESCE(pd_hrapp.title_th, ''::text) || ' '::text) || pd_hrapp.first_name_th) || ' '::text) || pd_hrapp.last_name_th) AS approver_name,
				po.date_contract_start AS po_date_contract_start,
				po.date_contract_end AS po_date_contract_end,
				po.date_approve AS po_date_approve,
				po.contract_id,
				po.order_id AS po_order_id,
				po.requisition_id,
				po.quote_id,
				po.id AS po_id
			   FROM (((((((stock_picking a
				 LEFT JOIN purchase_work_acceptance wa ON ((a.acceptance_id = wa.id)))
				 LEFT JOIN purchase_order po ON ((wa.order_id = po.id)))
				 LEFT JOIN purchase_requisition pd ON ((po.requisition_id = pd.id)))
				 LEFT JOIN res_users pd_requsr ON ((pd.request_uid = pd_requsr.id)))
				 LEFT JOIN issi_hr_employee_view pd_hrreq ON (((pd_requsr.login)::text = (pd_hrreq.employee_code)::text)))
				 LEFT JOIN res_users pd_appusr ON ((pd.assign_uid = pd_appusr.id)))
				 LEFT JOIN issi_hr_employee_view pd_hrapp ON (((pd_appusr.login)::text = (pd_hrapp.employee_code)::text)))
        )
        """ % self._table)
	
class issi_budget_summary_actual_view(models.Model):
    _name = 'issi.budget.summary.actual.view'
    _auto = False
    _description = 'issi_budget_summary_actual_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT fisyear.name AS fisyear,
				"left"((perd.name)::text, 2) AS period,
				aa.budget_commit_type,
				aa.charge_type,
				aa.budget_method,
				aa.doctype,
				aa.chart_view AS budget_view,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.project_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.section_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.code
						ELSE ''::character varying
					END AS source_budget_code,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.phase_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prj.project_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.name
						ELSE ''::character varying
					END AS source_budget_name,
				to_char((acmv.date_document)::timestamp with time zone, 'DD/MM/YYYY'::text) AS doc_date,
				to_char((acmv.date)::timestamp with time zone, 'DD/MM/YYYY'::text) AS posting_date,
					CASE
						WHEN (((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) THEN acmv.name
						ELSE aa.document
					END AS document,
				NULL::text AS item,
				acmvl.docline_seq AS amvl_item,
				aa.amount,
				aa.document_line AS detail,
					CASE
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'account_invoice'::text) AND (ref_inv.name IS NOT NULL)) THEN ref_inv.origin
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'account_invoice'::text) AND (ref_inv.name IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_salary_expense'::text) AND (ref_salary.number IS NOT NULL)) THEN ref_salary.number
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_salary_expense'::text) AND (ref_salary.number IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'interface_account_entry'::text) AND (ref_interface.number IS NOT NULL)) THEN ref_interface.number
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'interface_account_entry'::text) AND (ref_interface.number IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'stock_picking'::text) AND (ref_stock.name IS NOT NULL)) THEN ref_stock.origin
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'stock_picking'::text) AND (ref_stock.name IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_expense_expense'::text) AND (ref_exp.number IS NOT NULL)) THEN ref_exp.number
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_expense_expense'::text) AND (ref_exp.number IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'account_invoice'::text)) THEN ref_inv.origin
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'hr_salary_expense'::text)) THEN ref_salary.number
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'interface_account_entry'::text)) THEN ref_interface.number
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'stock_picking'::text)) THEN ref_stock.origin
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'hr_expense_expense'::text)) THEN ref_exp.number
						ELSE acmv.ref
					END AS ref_document,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ( SELECT to_char((pol.date_planned)::timestamp with time zone, 'DD/MM/YYYY'::text) AS to_char
						   FROM purchase_order_line pol
						  WHERE (ref_inv2.po_id = pol.order_id)
						 LIMIT 1)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ( SELECT to_char((pol.date_planned)::timestamp with time zone, 'DD/MM/YYYY'::text) AS to_char
						   FROM purchase_order_line pol
						  WHERE (ref_stock2.po_id = pol.order_id)
						 LIMIT 1)
						ELSE NULL::text
					END AS schedule_date,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN stock_po_con.poc_code
						WHEN (aa.document_ref = 'stock_picking'::text) THEN stock_po_con.poc_code
						ELSE NULL::character varying
					END AS po_contract,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN to_char((ref_inv2.po_date_contract_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN to_char((ref_stock2.po_date_contract_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE NULL::text
					END AS contract_start_date,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN to_char((ref_inv2.po_date_contract_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN to_char((ref_stock2.po_date_contract_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE NULL::text
					END AS contract_end_date,
				ml_prodcat.name AS product_category,
				ml_prod.id AS product_code,
				ml_prod_tm.name AS product_name,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN inv_pomethod.name
						WHEN (aa.document_ref = 'stock_picking'::text) THEN stock_pomethod.name
						ELSE NULL::character varying
					END AS purchasing_method,
				ag.code AS activity_group,
				ag.name AS activity_group_name,
				a.code AS activity,
				a.name AS activity_name,
				a_rpt.code AS activity_rpt,
				a_rpt.name AS activity_rpt_name,
				acct.code AS account_code,
				acct.name AS account_name,
				acmv_patrner.search_key AS partner_code,
				acmv_patrner.name AS partner_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.org_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_code
						ELSE org.code
					END AS org_code,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.org_name_short)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_name_short_en
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_name_short_en
						ELSE org.name_short
					END AS org_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.section_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.section_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.section_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.section_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.costcenter_code
						ELSE aa.chart_view
					END AS section,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN (invasset_sec.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prjsec.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (replace(sec2.section_name, '[ไม่ใช้งาน] '::text, ''::text))::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN (persec.costcenter_name)::character varying
						ELSE aa.chart_view
					END AS section_name,
				cctr.costcenter_code AS costcenter,
				cctr.costcenter_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.costcenter_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.costcenter_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.costcenter_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.costcenter_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.costcenter_code
						ELSE cctr.costcenter_code
					END AS costcenter_used,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN replace(prjcsec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN replace(invasset_sec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN replace(prjsec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN replace(sec2.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN replace(persec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						ELSE replace(cctr.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
					END AS costcenter_name_used,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.mission
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN (invasset_sec.mission_code)::character varying
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.mission
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.mission_code)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN 'IM'::character varying
						ELSE miss.name
					END AS mission,
				prj.functional_area_code AS functional_area,
				prj.functional_area_name,
				prj.program_group_code AS program_group,
				prj.program_group_name,
				prj.program_code AS program,
				prj.program_name,
				prj.project_group_code AS project_group,
				prj.project_group_name AS propect_group_name,
				prj.master_plan_code,
				prj.master_plan_name,
				prj.project_type_code AS project_type,
				prj.project_type_name,
				prj.operation_code AS project_operation_code,
				prj.operation_name AS project_operation_name,
				prj.fund_code AS project_fund_code,
				prj.fund_name AS project_fund_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN to_char((bgcon.phase_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.project_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE to_char((prj.project_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
					END AS project_date_start,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN to_char((bgcon.phase_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.project_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE to_char((prj.project_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
					END AS project_date_end,
				to_char((prj.date_start)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_start_spending,
				to_char((prj.date_end)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_end_spending,
					CASE
						WHEN (((aa.chart_view)::text = 'invest_construction'::text) AND ((bgcon.phase_state)::text = 'close'::text) AND (bgcon.phase_date_expansion IS NOT NULL)) THEN to_char((bgcon.phase_date_expansion)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.project_date_close)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE NULL::text
					END AS project_date_close,
				to_char((prj.project_date_close_cond)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_close_cond,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.pm_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.pm_code
						ELSE prj.pm_code
					END AS pm,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.pm_name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.pm_name
						ELSE prj.pm_name
					END AS pm_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.state
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.pb2_status
						ELSE prj.pb2_status
					END AS project_status,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.sector_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.sector_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.sector_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.sector_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.sector_code
						ELSE sec2.sector_code
					END AS sector,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.sector_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.sector_name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.sector_name
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.sector_name
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.sector_name
						ELSE sec2.sector_name
					END AS sector_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.subsector_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.subsector_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.subsector_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.subsector_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.subsector_code
						ELSE sec2.subsector_code
					END AS sub_sector,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN (invasset_sec.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prjsec.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN (persec.subsector_name)::character varying
						ELSE aa.chart_view
					END AS sub_sector_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.division_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.division_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.division_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.division_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.division_code
						ELSE sec2.division_code
					END AS division,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.division_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.division_name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.division_name
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.division_name
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.division_name
						ELSE sec2.division_name
					END AS division_name,
					CASE
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsecpg.code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN ressecpg.code
						ELSE secpg.code
					END AS section_program,
					CASE
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsecpg.name
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN ressecpg.name
						ELSE secpg.name
					END AS section_program_name,
				bgcon.construction_code AS project_c_code,
				bgcon.construction_name AS project_c_name,
				to_char((bgcon.date_start)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_c_date_start,
				to_char((bgcon.date_end)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_c_date_end,
				to_char((bgcon.date_expansion)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_c_date_expansion,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.requested_by
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN sal_hrreq.employee_code
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.requested_by
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrreq.employee_code
						ELSE NULL::character varying
					END AS request_by,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.requested_by_name
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN ((((COALESCE(sal_hrreq.title_th, ''::text) || ' '::text) || sal_hrreq.first_name_th) || ' '::text) || sal_hrreq.last_name_th)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.requested_by_name
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrreq.title_th, ''::text) || ' '::text) || exp_hrreq.first_name_th) || ' '::text) || exp_hrreq.last_name_th)
						ELSE NULL::text
					END AS request_by_name,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.approver
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN sal_hrapp.employee_code
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.approver
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrapp.employee_code
						ELSE NULL::character varying
					END AS approver,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.approver_name
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN ((((COALESCE(sal_hrapp.title_th, ''::text) || ' '::text) || sal_hrapp.first_name_th) || ' '::text) || sal_hrapp.last_name_th)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.approver_name
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrapp.title_th, ''::text) || ' '::text) || exp_hrapp.first_name_th) || ' '::text) || exp_hrapp.last_name_th)
						ELSE NULL::text
					END AS approver_name,
					CASE
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN sal_hrpre.employee_code
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrpre.employee_code
						ELSE NULL::character varying
					END AS prepared_by,
					CASE
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN ((((COALESCE(sal_hrpre.title_th, ''::text) || ' '::text) || sal_hrpre.first_name_th) || ' '::text) || sal_hrpre.last_name_th)
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrpre.title_th, ''::text) || ' '::text) || exp_hrpre.first_name_th) || ' '::text) || exp_hrpre.last_name_th)
						ELSE NULL::text
					END AS prepared_by_name,
				aa.document_ref
			   FROM (((((((((((((((((((((((((((((((((((((((((((((((((((((((((issi_budget_summary_consume_view aa
				 LEFT JOIN account_period perd ON ((aa.period_id = perd.id)))
				 LEFT JOIN account_fiscalyear fisyear ON ((aa.fiscalyear_id = fisyear.id)))
				 LEFT JOIN account_activity_group ag ON ((aa.activity_group_id = ag.id)))
				 LEFT JOIN account_activity a ON ((aa.activity_id = a.id)))
				 LEFT JOIN account_activity a_rpt ON ((aa.activity_rpt_id = a_rpt.id)))
				 LEFT JOIN account_account acct ON ((aa.account_id = acct.id)))
				 LEFT JOIN account_account acct_rpt ON ((a_rpt.account_id = acct_rpt.id)))
				 LEFT JOIN stock_picking ref_stock ON ((aa.document_ref_id = (ref_stock.id)::numeric)))
				 LEFT JOIN account_invoice ref_inv ON ((aa.document_ref_id = (ref_inv.id)::numeric)))
				 LEFT JOIN hr_salary_expense ref_salary ON ((aa.document_ref_id = (ref_salary.id)::numeric)))
				 LEFT JOIN interface_account_entry ref_interface ON ((aa.document_ref_id = (ref_interface.id)::numeric)))
				 LEFT JOIN hr_expense_expense ref_exp ON ((aa.document_ref_id = (ref_exp.id)::numeric)))
				 LEFT JOIN issi_actual_ref_invoice_view ref_inv2 ON ((aa.document_ref_id = (ref_inv2.invoice_id)::numeric)))
				 LEFT JOIN issi_actual_ref_stock_picking_view ref_stock2 ON ((aa.document_ref_id = (ref_stock2.stock_picking_id)::numeric)))
				 LEFT JOIN account_move_line acmvl ON ((aa.move_id = acmvl.id)))
				 LEFT JOIN account_move acmv ON ((acmvl.move_id = acmv.id)))
				 LEFT JOIN res_partner acmv_patrner ON ((acmv.partner_id = acmv_patrner.id)))
				 LEFT JOIN product_product ml_prod ON ((acmvl.product_id = ml_prod.id)))
				 LEFT JOIN product_template ml_prod_tm ON ((ml_prod.product_tmpl_id = ml_prod_tm.id)))
				 LEFT JOIN product_category ml_prodcat ON ((ml_prod_tm.categ_id = ml_prodcat.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrreq ON ((ref_exp.employee_id = exp_hrreq.id)))
				 LEFT JOIN res_users exp_usrapp ON ((ref_exp.approver_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrapp ON (((exp_usrapp.login)::text = (exp_hrapp.employee_code)::text)))
				 LEFT JOIN res_users exp_usrpre ON ((ref_exp.user_id = exp_usrpre.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrpre ON (((exp_usrpre.login)::text = (exp_hrpre.employee_code)::text)))
				 LEFT JOIN res_users sal_usrreq ON ((ref_salary.submit_user_id = sal_usrreq.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrreq ON (((sal_usrreq.login)::text = (sal_hrreq.employee_code)::text)))
				 LEFT JOIN res_users sal_usrapp ON ((ref_salary.approve_user_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrapp ON (((exp_usrapp.login)::text = (sal_hrapp.employee_code)::text)))
				 LEFT JOIN res_users sal_usrpre ON ((ref_salary.user_id = exp_usrpre.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrpre ON (((exp_usrpre.login)::text = (sal_hrpre.employee_code)::text)))
				 LEFT JOIN purchase_contract stock_po_con ON ((ref_stock2.contract_id = stock_po_con.id)))
				 LEFT JOIN purchase_contract inv_po_con ON ((ref_inv2.contract_id = stock_po_con.id)))
				 LEFT JOIN purchase_order stock_rfq ON ((ref_stock2.quote_id = stock_rfq.id)))
				 LEFT JOIN purchase_requisition stoc_pd ON ((stock_rfq.requisition_id = stoc_pd.id)))
				 LEFT JOIN purchase_method stock_pomethod ON ((stoc_pd.purchase_method_id = stock_pomethod.id)))
				 LEFT JOIN purchase_order inv_rfq ON ((ref_inv2.quote_id = inv_rfq.id)))
				 LEFT JOIN purchase_requisition inv_pd ON ((inv_rfq.requisition_id = inv_pd.id)))
				 LEFT JOIN purchase_method inv_pomethod ON ((inv_pd.purchase_method_id = inv_pomethod.id)))
				 LEFT JOIN res_mission miss ON ((aa.mission_id = miss.id)))
				 LEFT JOIN res_org org ON ((aa.org_id = org.id)))
				 LEFT JOIN etl_issi_m_section sec2 ON ((aa.section_id = sec2.section_id)))
				 LEFT JOIN res_section res_sec ON ((aa.section_id = res_sec.id)))
				 LEFT JOIN res_section_program ressecpg ON ((res_sec.section_program_id = ressecpg.id)))
				 LEFT JOIN res_section_program secpg ON ((aa.section_program_id = secpg.id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((aa.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN etl_issi_m_project prj ON ((aa.project_id = prj.pb2_project_id)))
				 LEFT JOIN etl_issi_m_section prjsec ON ((prj.pm_section_id = prjsec.section_id)))
				 LEFT JOIN res_project res_prj ON ((aa.project_id = res_prj.id)))
				 LEFT JOIN res_program prjpg ON ((res_prj.program_id = prjpg.id)))
				 LEFT JOIN res_section_program prjsecpg ON ((prjpg.section_program_id = prjsecpg.id)))
				 LEFT JOIN issi_m_investment_construction_phase_view bgcon ON ((aa.invest_construction_phase_id = bgcon.invest_construction_phase_id)))
				 LEFT JOIN etl_issi_m_section prjcsec ON ((bgcon.pm_section_id = prjcsec.section_id)))
				 LEFT JOIN res_invest_asset bgasset ON ((aa.invest_asset_id = bgasset.id)))
				 LEFT JOIN etl_issi_m_section invasset_sec ON ((bgasset.owner_section_id = invasset_sec.section_id)))
				 LEFT JOIN res_personnel_costcenter budper ON ((aa.personnel_costcenter_id = budper.id)))
				 LEFT JOIN issi_m_personel_costcenter_view persec ON ((budper.id = persec.id)))
			  WHERE (((aa.budget_commit_type)::text = 'actual'::text) AND (aa.amount <> (0)::numeric))	
        )
        """ % self._table)

class issi_budget_summary_commit_view(models.Model):
    _name = 'issi.budget.summary.commit.view'
    _auto = False
    _description = 'issi_budget_summary_commit_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT fisyear.name AS fisyear,
				"left"((perd.name)::text, 2) AS period,
				aa.budget_commit_type,
				aa.charge_type,
				aa.budget_method,
				aa.doctype,
				aa.chart_view AS budget_view,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.project_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.section_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.code
						ELSE ''::character varying
					END AS source_budget_code,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.phase_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prj.project_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.name
						ELSE ''::character varying
					END AS source_budget_name,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN to_char((pr.date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN to_char(po.date_order, 'DD/MM/YYYY'::text)
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN to_char((exp.date)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE ''::text
					END AS doc_date,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN to_char((pr.date_approve)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN to_char(po.date_order, 'DD/MM/YYYY'::text)
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN to_char((exp.date)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE ''::text
					END AS posting_date,
				aa.document,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_line.docline_seq
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN po_line.docline_seq
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN exp_line.docline_seq
						ELSE NULL::integer
					END AS item,
				aa.amount,
				aa.document_line AS detail,
				popr.name AS ref_document,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN to_char((pr_line.date_required)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN to_char((po_line.date_planned)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE NULL::text
					END AS schedule_date,
				popr_line.id,
				po_con.poc_code AS po_contract,
				to_char((po.date_contract_start)::timestamp with time zone, 'DD/MM/YYYY'::text) AS contract_start_date,
				to_char((po.date_contract_end)::timestamp with time zone, 'DD/MM/YYYY'::text) AS contract_end_date,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_prodcat.name
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN po_prodcat.name
						ELSE NULL::character varying
					END AS product_category,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_prod.id
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN po_prod.id
						ELSE NULL::integer
					END AS product_code,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN COALESCE(pr_prod_tm.name, pr_line.name)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN COALESCE(po_prod_tm.name, (po_line.name)::character varying)
						ELSE NULL::character varying
					END AS product_name,
				pometh.name AS purchasing_method,
				ag.code AS activity_group,
				ag.name AS activity_group_name,
				a.code AS activity,
				a.name AS activity_name,
				a_rpt.code AS activity_rpt,
				a_rpt.name AS activity_rpt_name,
				acct.code AS account_code,
				acct.name AS account_name,
				po_partner.search_key AS partner_code,
				po_partner.name AS partner_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.org_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_code
						ELSE org.code
					END AS org_code,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.org_name_short)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_name_short_en
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_name_short_en
						ELSE org.name_short
					END AS org_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.section_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.section_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.section_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.section_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.costcenter_code
						ELSE aa.chart_view
					END AS section,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN (invasset_sec.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prjsec.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (replace(sec2.section_name, '[ไม่ใช้งาน] '::text, ''::text))::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN (persec.costcenter_name)::character varying
						ELSE aa.chart_view
					END AS section_name,
				cctr.costcenter_code AS costcenter,
				cctr.costcenter_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.costcenter_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.costcenter_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.costcenter_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.costcenter_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.costcenter_code
						ELSE cctr.costcenter_code
					END AS costcenter_used,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN replace(prjcsec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN replace(invasset_sec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN replace(prjsec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN replace(sec2.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN replace(persec.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
						ELSE replace(cctr.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text)
					END AS costcenter_name_used,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.mission
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN (invasset_sec.mission_code)::character varying
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.mission
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.mission_code)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN 'IM'::character varying
						ELSE miss.name
					END AS mission,
				prj.functional_area_code AS functional_area,
				prj.functional_area_name,
				prj.program_group_code AS program_group,
				prj.program_group_name,
				prj.program_code AS program,
				prj.program_name,
				prj.project_group_code AS project_group,
				prj.project_group_name AS propect_group_name,
				prj.master_plan_code,
				prj.master_plan_name,
				prj.project_type_code AS project_type,
				prj.project_type_name,
				prj.operation_code AS project_operation_code,
				prj.operation_name AS project_operation_name,
				prj.fund_code AS project_fund_code,
				prj.fund_name AS project_fund_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN to_char((bgcon.phase_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.project_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE to_char((prj.project_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
					END AS project_date_start,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN to_char((bgcon.phase_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.project_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE to_char((prj.project_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
					END AS project_date_end,
				to_char((prj.date_start)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_start_spending,
				to_char((prj.date_end)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_end_spending,
					CASE
						WHEN (((aa.chart_view)::text = 'invest_construction'::text) AND ((bgcon.phase_state)::text = 'close'::text) AND (bgcon.phase_date_expansion IS NOT NULL)) THEN to_char((bgcon.phase_date_expansion)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.project_date_close)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE NULL::text
					END AS project_date_close,
				to_char((prj.project_date_close_cond)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_close_cond,
				to_char((prj.date_approve)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_approved,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN to_char((bgcon.phase_contract_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.contract_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE to_char((prj.contract_date_start)::timestamp with time zone, 'DD/MM/YYYY'::text)
					END AS contract_date_start,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN to_char((bgcon.phase_contract_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN to_char((prj.contract_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
						ELSE to_char((prj.contract_date_end)::timestamp with time zone, 'DD/MM/YYYY'::text)
					END AS contract_date_end,
				to_char((prj.project_date_end_proposal)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_end_proposal,
				to_char((prj.project_date_terminate)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_date_terminate,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.pm_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.pm_code
						ELSE prj.pm_code
					END AS pm,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.pm_name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.pm_name
						ELSE prj.pm_name
					END AS pm_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.state
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.pb2_status
						ELSE prj.pb2_status
					END AS project_status,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.sector_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.sector_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.sector_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.sector_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.sector_code
						ELSE sec2.sector_code
					END AS sector,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.sector_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.sector_name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.sector_name
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.sector_name
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.sector_name
						ELSE sec2.sector_name
					END AS sector_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.subsector_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.subsector_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.subsector_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.subsector_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.subsector_code
						ELSE sec2.subsector_code
					END AS sub_sector,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN (invasset_sec.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prjsec.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.subsector_name)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN (persec.subsector_name)::character varying
						ELSE aa.chart_view
					END AS sub_sector_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.division_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.division_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.division_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.division_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.division_code
						ELSE sec2.division_code
					END AS division,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.division_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.division_name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.division_name
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.division_name
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.division_name
						ELSE sec2.division_name
					END AS division_name,
					CASE
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsecpg.code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN ressecpg.code
						ELSE secpg.code
					END AS section_program,
					CASE
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsecpg.name
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN ressecpg.name
						ELSE secpg.name
					END AS section_program_name,
				bgcon.construction_code AS project_c_code,
				bgcon.construction_name AS project_c_name,
				to_char((bgcon.date_start)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_c_date_start,
				to_char((bgcon.date_end)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_c_date_end,
				to_char((bgcon.date_expansion)::timestamp with time zone, 'DD/MM/YYYY'::text) AS project_c_date_expansion,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_hrreq.employee_code
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN popr_hrreq.employee_code
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN exp_hrreq.employee_code
						ELSE NULL::character varying
					END AS requested_by,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN ((((COALESCE(pr_hrreq.title_th, ''::text) || ' '::text) || pr_hrreq.first_name_th) || ' '::text) || pr_hrreq.last_name_th)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN ((((COALESCE(popr_hrreq.title_th, ''::text) || ' '::text) || popr_hrreq.first_name_th) || ' '::text) || popr_hrreq.last_name_th)
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN ((((COALESCE(exp_hrreq.title_th, ''::text) || ' '::text) || exp_hrreq.first_name_th) || ' '::text) || exp_hrreq.last_name_th)
						ELSE NULL::text
					END AS requested_by_name,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_hrapp.employee_code
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN popr_hrapp.employee_code
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN exp_hrapp.employee_code
						ELSE NULL::character varying
					END AS approver,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN ((((COALESCE(pr_hrapp.title_th, ''::text) || ' '::text) || pr_hrapp.first_name_th) || ' '::text) || pr_hrapp.last_name_th)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN ((((COALESCE(popr_hrapp.title_th, ''::text) || ' '::text) || popr_hrapp.first_name_th) || ' '::text) || popr_hrapp.last_name_th)
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN ((((COALESCE(exp_hrapp.title_th, ''::text) || ' '::text) || exp_hrapp.first_name_th) || ' '::text) || exp_hrapp.last_name_th)
						ELSE NULL::text
					END AS approver_name,
				exp_hrpre.employee_code AS prepared_by,
				((((COALESCE(exp_hrpre.title_th, ''::text) || ' '::text) || exp_hrpre.first_name_th) || ' '::text) || exp_hrpre.last_name_th) AS prepared_by_name
			   FROM ((((((((((((((((((((((((((((((((((((((((((((((((((((((((((issi_budget_summary_consume_view aa
				 LEFT JOIN account_period perd ON ((aa.period_id = perd.id)))
				 LEFT JOIN account_fiscalyear fisyear ON ((aa.fiscalyear_id = fisyear.id)))
				 LEFT JOIN account_activity_group ag ON ((aa.activity_group_id = ag.id)))
				 LEFT JOIN account_activity a ON ((aa.activity_id = a.id)))
				 LEFT JOIN account_activity a_rpt ON ((aa.activity_rpt_id = a_rpt.id)))
				 LEFT JOIN account_account acct ON ((aa.account_id = acct.id)))
				 LEFT JOIN account_account acct_rpt ON ((a_rpt.account_id = acct_rpt.id)))
				 LEFT JOIN res_mission miss ON ((aa.mission_id = miss.id)))
				 LEFT JOIN res_org org ON ((aa.org_id = org.id)))
				 LEFT JOIN etl_issi_m_section sec2 ON ((aa.section_id = sec2.section_id)))
				 LEFT JOIN res_section res_sec ON ((aa.section_id = res_sec.id)))
				 LEFT JOIN res_section_program ressecpg ON ((res_sec.section_program_id = ressecpg.id)))
				 LEFT JOIN res_section_program secpg ON ((aa.section_program_id = secpg.id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((aa.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN etl_issi_m_project prj ON ((aa.project_id = prj.pb2_project_id)))
				 LEFT JOIN etl_issi_m_section prjsec ON ((prj.pm_section_id = prjsec.section_id)))
				 LEFT JOIN res_project res_prj ON ((aa.project_id = res_prj.id)))
				 LEFT JOIN res_program prjpg ON ((res_prj.program_id = prjpg.id)))
				 LEFT JOIN res_section_program prjsecpg ON ((prjpg.section_program_id = prjsecpg.id)))
				 LEFT JOIN issi_m_investment_construction_phase_view bgcon ON ((aa.invest_construction_phase_id = bgcon.invest_construction_phase_id)))
				 LEFT JOIN etl_issi_m_section prjcsec ON ((bgcon.pm_section_id = prjcsec.section_id)))
				 LEFT JOIN res_invest_asset bgasset ON ((aa.invest_asset_id = bgasset.id)))
				 LEFT JOIN etl_issi_m_section invasset_sec ON ((bgasset.owner_section_id = invasset_sec.section_id)))
				 LEFT JOIN res_personnel_costcenter budper ON ((aa.personnel_costcenter_id = budper.id)))
				 LEFT JOIN issi_m_personel_costcenter_view persec ON ((budper.id = persec.id)))
				 LEFT JOIN purchase_request_line pr_line ON ((aa.purchase_request_line_id = pr_line.id)))
				 LEFT JOIN purchase_request pr ON ((pr_line.request_id = pr.id)))
				 LEFT JOIN product_product pr_prod ON ((pr_line.product_id = pr_prod.id)))
				 LEFT JOIN product_template pr_prod_tm ON ((pr_prod.product_tmpl_id = pr_prod_tm.id)))
				 LEFT JOIN product_category pr_prodcat ON ((pr_prod_tm.categ_id = pr_prodcat.id)))
				 LEFT JOIN res_users pr_usreq ON ((pr.requested_by = pr_usreq.id)))
				 LEFT JOIN issi_hr_employee_view pr_hrreq ON (((pr_usreq.login)::text = (pr_hrreq.employee_code)::text)))
				 LEFT JOIN res_users pr_usrapp ON ((pr.assigned_to = pr_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view pr_hrapp ON (((pr_usrapp.login)::text = (pr_hrapp.employee_code)::text)))
				 LEFT JOIN purchase_order_line po_line ON ((aa.purchase_line_id = po_line.id)))
				 LEFT JOIN purchase_order po ON ((po_line.order_id = po.id)))
				 LEFT JOIN purchase_request_purchase_order_line_rel prpo_rel ON ((po_line.id = prpo_rel.purchase_order_line_id)))
				 LEFT JOIN purchase_request_line popr_line ON ((prpo_rel.purchase_request_line_id = popr_line.id)))
				 LEFT JOIN purchase_request popr ON ((popr_line.request_id = popr.id)))
				 LEFT JOIN purchase_order po_rfq ON ((po.quote_id = po_rfq.id)))
				 LEFT JOIN purchase_requisition poreq ON ((po_rfq.requisition_id = poreq.id)))
				 LEFT JOIN purchase_method pometh ON ((poreq.purchase_method_id = pometh.id)))
				 LEFT JOIN purchase_contract po_con ON ((po.contract_id = po_con.id)))
				 LEFT JOIN product_product po_prod ON ((po_line.product_id = po_prod.id)))
				 LEFT JOIN product_template po_prod_tm ON ((po_prod.product_tmpl_id = po_prod_tm.id)))
				 LEFT JOIN product_category po_prodcat ON ((po_prod_tm.categ_id = po_prodcat.id)))
				 LEFT JOIN res_partner po_partner ON ((po.partner_id = po_partner.id)))
				 LEFT JOIN res_users popr_usreq ON ((popr.requested_by = popr_usreq.id)))
				 LEFT JOIN issi_hr_employee_view popr_hrreq ON (((popr_usreq.login)::text = (popr_hrreq.employee_code)::text)))
				 LEFT JOIN res_users popr_usrapp ON ((popr.assigned_to = popr_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view popr_hrapp ON (((popr_usrapp.login)::text = (popr_hrapp.employee_code)::text)))
				 LEFT JOIN hr_expense_line exp_line ON ((aa.expense_line_id = exp_line.id)))
				 LEFT JOIN hr_expense_expense exp ON ((exp_line.expense_id = exp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrreq ON ((exp.employee_id = exp_hrreq.id)))
				 LEFT JOIN res_users exp_usrapp ON ((exp.approver_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrapp ON (((exp_usrapp.login)::text = (exp_hrapp.employee_code)::text)))
				 LEFT JOIN res_users exp_usrpre ON ((exp.user_id = exp_usrpre.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrpre ON (((exp_usrpre.login)::text = (exp_hrpre.employee_code)::text)))
			  WHERE (((aa.budget_commit_type)::text <> 'actual'::text) AND (aa.amount <> (0)::numeric))
        )
        """ % self._table)
	
class etl_issi_budget_actual(models.Model):
    _name = 'etl.issi.budget.actual'
    _auto = False
    _description = 'etl_issi_budget_actual'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT aa.budget_commit_type,
				aa.charge_type,
				aa.budget_method,
				aa.doctype,
				aa.chart_view,
				fisyear.name AS fisyear,
				perd.name AS period,
					CASE
						WHEN (((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) THEN acmv.name
						ELSE aa.document
					END AS document,
				aa.document_line AS detail,
				ag.code AS activity_group,
				ag.name AS activity_group_name,
				a_rpt.code AS activity,
				a_rpt.name AS activity_name,
				a_rpt.code AS activity_rpt,
				a_rpt.name AS activity_rpt_name,
				sec2.section_code AS section,
				sec2.section_name,
				prj.project_code AS project,
				prj.project_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.org_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_code
						ELSE org.code
					END AS org,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.org_name_short)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_name_short_en
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_name_short_en
						ELSE org.name_short
					END AS org_name,
				cctr.costcenter_code AS costcenter,
				cctr.costcenter_name,
				aa.amount,
				acmv.date_document AS date_doc,
				replace(aa.document_ref, '_'::text, '.'::text) AS document_ref,
				NULL::text AS document_ref_id,
				NULL::text AS source_document_type,
					CASE
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'account_invoice'::text) AND (ref_inv.name IS NOT NULL)) THEN ref_inv.origin
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'account_invoice'::text) AND (ref_inv.name IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_salary_expense'::text) AND (ref_salary.number IS NOT NULL)) THEN ref_salary.number
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_salary_expense'::text) AND (ref_salary.number IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'interface_account_entry'::text) AND (ref_interface.number IS NOT NULL)) THEN ref_interface.number
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'interface_account_entry'::text) AND (ref_interface.number IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'stock_picking'::text) AND (ref_stock.name IS NOT NULL)) THEN ref_stock.origin
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'stock_picking'::text) AND (ref_stock.name IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_expense_expense'::text) AND (ref_exp.number IS NOT NULL)) THEN ref_exp.number
						WHEN ((((aa.document)::text = '/'::text) OR ((aa.document)::text = ''::text) OR (aa.document IS NULL)) AND (aa.document_ref = 'hr_expense_expense'::text) AND (ref_exp.number IS NULL)) THEN acmv.ref
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'account_invoice'::text)) THEN ref_inv.origin
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'hr_salary_expense'::text)) THEN ref_salary.number
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'interface_account_entry'::text)) THEN ref_interface.number
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'stock_picking'::text)) THEN ref_stock.origin
						WHEN ((((aa.document)::text <> '/'::text) OR ((aa.document)::text <> ''::text) OR (aa.document IS NOT NULL)) AND (aa.document_ref = 'hr_expense_expense'::text)) THEN ref_exp.number
						ELSE acmv.ref
					END AS source_document,
				NULL::text AS verify_employee,
				NULL::text AS verify_employee_name,
				NULL::text AS response_employee,
				NULL::text AS response_employee_name,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.requested_by
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN sal_hrreq.employee_code
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.requested_by
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrreq.employee_code
						ELSE NULL::character varying
					END AS emp_employee,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.requested_by_name
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN ((((COALESCE(sal_hrreq.title_th, ''::text) || ' '::text) || sal_hrreq.first_name_th) || ' '::text) || sal_hrreq.last_name_th)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.requested_by_name
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrreq.title_th, ''::text) || ' '::text) || exp_hrreq.first_name_th) || ' '::text) || exp_hrreq.last_name_th)
						ELSE NULL::text
					END AS emp_employee_name,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.approver
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN sal_hrapp.employee_code
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.approver
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrapp.employee_code
						ELSE NULL::character varying
					END AS approver_employee,
					CASE
						WHEN (aa.document_ref = 'account_invoice'::text) THEN ref_inv2.approver_name
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN ((((COALESCE(sal_hrapp.title_th, ''::text) || ' '::text) || sal_hrapp.first_name_th) || ' '::text) || sal_hrapp.last_name_th)
						WHEN (aa.document_ref = 'stock_picking'::text) THEN ref_stock2.approver_name
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrapp.title_th, ''::text) || ' '::text) || exp_hrapp.first_name_th) || ' '::text) || exp_hrapp.last_name_th)
						ELSE NULL::text
					END AS approver_employee_name,
					CASE
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN sal_hrpre.employee_code
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN exp_hrpre.employee_code
						ELSE NULL::character varying
					END AS user_employee,
					CASE
						WHEN (aa.document_ref = 'hr_salary_expense'::text) THEN ((((COALESCE(sal_hrpre.title_th, ''::text) || ' '::text) || sal_hrpre.first_name_th) || ' '::text) || sal_hrpre.last_name_th)
						WHEN (aa.document_ref = 'hr_expense_expense'::text) THEN ((((COALESCE(exp_hrpre.title_th, ''::text) || ' '::text) || exp_hrpre.first_name_th) || ' '::text) || exp_hrpre.last_name_th)
						ELSE NULL::text
					END AS user_employee_name,
				acmv.date AS approve_date,
				NULL::text AS source_system,
				'AC'::text AS source_type,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.project_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.section_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.code
						ELSE ''::character varying
					END AS source_budget_code,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.phase_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prj.project_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.name
						ELSE ''::character varying
					END AS source_budget_name,
				acmv.date AS posting_date,
				job.code AS job_order,
				job.name AS job_order_name,
				jobtype.code AS job_order_type,
				jobtype.name AS job_order_type_name
			   FROM (((((((((((((((((((((((((((((((((((((((((((((((((((((((((((issi_budget_summary_consume_view aa
				 LEFT JOIN account_period perd ON ((aa.period_id = perd.id)))
				 LEFT JOIN account_fiscalyear fisyear ON ((aa.fiscalyear_id = fisyear.id)))
				 LEFT JOIN account_activity_group ag ON ((aa.activity_group_id = ag.id)))
				 LEFT JOIN account_activity a ON ((aa.activity_id = a.id)))
				 LEFT JOIN account_activity a_rpt ON ((aa.activity_rpt_id = a_rpt.id)))
				 LEFT JOIN account_account acct ON ((aa.account_id = acct.id)))
				 LEFT JOIN account_account acct_rpt ON ((a_rpt.account_id = acct_rpt.id)))
				 LEFT JOIN stock_picking ref_stock ON ((aa.document_ref_id = (ref_stock.id)::numeric)))
				 LEFT JOIN account_invoice ref_inv ON ((aa.document_ref_id = (ref_inv.id)::numeric)))
				 LEFT JOIN hr_salary_expense ref_salary ON ((aa.document_ref_id = (ref_salary.id)::numeric)))
				 LEFT JOIN interface_account_entry ref_interface ON ((aa.document_ref_id = (ref_interface.id)::numeric)))
				 LEFT JOIN hr_expense_expense ref_exp ON ((aa.document_ref_id = (ref_exp.id)::numeric)))
				 LEFT JOIN issi_actual_ref_invoice_view ref_inv2 ON ((aa.document_ref_id = (ref_inv2.invoice_id)::numeric)))
				 LEFT JOIN issi_actual_ref_stock_picking_view ref_stock2 ON ((aa.document_ref_id = (ref_stock2.stock_picking_id)::numeric)))
				 LEFT JOIN account_move_line acmvl ON ((aa.move_id = acmvl.id)))
				 LEFT JOIN account_move acmv ON ((acmvl.move_id = acmv.id)))
				 LEFT JOIN res_partner acmv_patrner ON ((acmv.partner_id = acmv_patrner.id)))
				 LEFT JOIN product_product ml_prod ON ((acmvl.product_id = ml_prod.id)))
				 LEFT JOIN product_template ml_prod_tm ON ((ml_prod.product_tmpl_id = ml_prod_tm.id)))
				 LEFT JOIN product_category ml_prodcat ON ((ml_prod_tm.categ_id = ml_prodcat.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrreq ON ((ref_exp.employee_id = exp_hrreq.id)))
				 LEFT JOIN res_users exp_usrapp ON ((ref_exp.approver_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrapp ON (((exp_usrapp.login)::text = (exp_hrapp.employee_code)::text)))
				 LEFT JOIN res_users exp_usrpre ON ((ref_exp.user_id = exp_usrpre.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrpre ON (((exp_usrpre.login)::text = (exp_hrpre.employee_code)::text)))
				 LEFT JOIN res_users sal_usrreq ON ((ref_salary.submit_user_id = sal_usrreq.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrreq ON (((sal_usrreq.login)::text = (sal_hrreq.employee_code)::text)))
				 LEFT JOIN res_users sal_usrapp ON ((ref_salary.approve_user_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrapp ON (((exp_usrapp.login)::text = (sal_hrapp.employee_code)::text)))
				 LEFT JOIN res_users sal_usrpre ON ((ref_salary.user_id = exp_usrpre.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrpre ON (((exp_usrpre.login)::text = (sal_hrpre.employee_code)::text)))
				 LEFT JOIN purchase_contract stock_po_con ON ((ref_stock2.contract_id = stock_po_con.id)))
				 LEFT JOIN purchase_contract inv_po_con ON ((ref_inv2.contract_id = stock_po_con.id)))
				 LEFT JOIN purchase_order stock_rfq ON ((ref_stock2.quote_id = stock_rfq.id)))
				 LEFT JOIN purchase_requisition stoc_pd ON ((stock_rfq.requisition_id = stoc_pd.id)))
				 LEFT JOIN purchase_method stock_pomethod ON ((stoc_pd.purchase_method_id = stock_pomethod.id)))
				 LEFT JOIN purchase_order inv_rfq ON ((ref_inv2.quote_id = inv_rfq.id)))
				 LEFT JOIN purchase_requisition inv_pd ON ((inv_rfq.requisition_id = inv_pd.id)))
				 LEFT JOIN purchase_method inv_pomethod ON ((inv_pd.purchase_method_id = inv_pomethod.id)))
				 LEFT JOIN res_mission miss ON ((aa.mission_id = miss.id)))
				 LEFT JOIN res_org org ON ((aa.org_id = org.id)))
				 LEFT JOIN etl_issi_m_section sec2 ON ((aa.section_id = sec2.section_id)))
				 LEFT JOIN res_section res_sec ON ((aa.section_id = res_sec.id)))
				 LEFT JOIN res_section_program ressecpg ON ((res_sec.section_program_id = ressecpg.id)))
				 LEFT JOIN res_section_program secpg ON ((aa.section_program_id = secpg.id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((aa.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN etl_issi_m_project prj ON ((aa.project_id = prj.pb2_project_id)))
				 LEFT JOIN etl_issi_m_section prjsec ON ((prj.pm_section_id = prjsec.section_id)))
				 LEFT JOIN res_project res_prj ON ((aa.project_id = res_prj.id)))
				 LEFT JOIN res_program prjpg ON ((res_prj.program_id = prjpg.id)))
				 LEFT JOIN res_section_program prjsecpg ON ((prjpg.section_program_id = prjsecpg.id)))
				 LEFT JOIN issi_m_investment_construction_phase_view bgcon ON ((aa.invest_construction_phase_id = bgcon.invest_construction_phase_id)))
				 LEFT JOIN etl_issi_m_section prjcsec ON ((bgcon.pm_section_id = prjcsec.section_id)))
				 LEFT JOIN res_invest_asset bgasset ON ((aa.invest_asset_id = bgasset.id)))
				 LEFT JOIN etl_issi_m_section invasset_sec ON ((bgasset.owner_section_id = invasset_sec.section_id)))
				 LEFT JOIN res_personnel_costcenter budper ON ((aa.personnel_costcenter_id = budper.id)))
				 LEFT JOIN issi_m_personel_costcenter_view persec ON ((budper.id = persec.id)))
				 LEFT JOIN cost_control job ON ((aa.cost_control_id = job.id)))
				 LEFT JOIN cost_control_type jobtype ON ((aa.cost_control_type_id = jobtype.id)))
			  WHERE (((aa.budget_commit_type)::text = 'actual'::text) AND (aa.amount <> (0)::numeric))
        )
        """ % self._table)

class etl_issi_budget_commit(models.Model):
    _name = 'etl.issi.budget.commit'
    _auto = False
    _description = 'etl_issi_budget_commit'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT aa.budget_commit_type,
				aa.charge_type,
				aa.budget_method,
				aa.doctype,
				aa.chart_view,
				fisyear.name AS fisyear,
				perd.name AS period,
				aa.document,
				aa.document_line AS detail,
				ag.code AS activity_group,
				ag.name AS activity_group_name,
				a_rpt.code AS activity,
				a_rpt.name AS activity_name,
				sec2.section_code AS section,
				sec2.section_name,
				prj.project_code AS project,
				prj.project_name,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN prjcsec.org_code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_code
						ELSE org.code
					END AS org,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN (prjcsec.org_name_short)::character varying
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN invasset_sec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prjsec.org_name_short_en
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.org_name_short_en
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN persec.org_name_short_en
						ELSE org.name_short
					END AS org_name,
				cctr.costcenter_code AS costcenter,
				cctr.costcenter_name,
				popr.name AS ref_document,
				NULL::text AS ref_document_seq,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN (pr.date_approve)::timestamp without time zone
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN po.date_order
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN (exp.date)::timestamp without time zone
						ELSE NULL::timestamp without time zone
					END AS approve_date,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_hrreq.employee_code
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN popr_hrreq.employee_code
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN exp_hrreq.employee_code
						ELSE NULL::character varying
					END AS employee_request,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN ((((COALESCE(pr_hrreq.title_th, ''::text) || ' '::text) || pr_hrreq.first_name_th) || ' '::text) || pr_hrreq.last_name_th)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN ((((COALESCE(popr_hrreq.title_th, ''::text) || ' '::text) || popr_hrreq.first_name_th) || ' '::text) || popr_hrreq.last_name_th)
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN ((((COALESCE(exp_hrreq.title_th, ''::text) || ' '::text) || exp_hrreq.first_name_th) || ' '::text) || exp_hrreq.last_name_th)
						ELSE NULL::text
					END AS employee_request_name,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN pr_hrapp.employee_code
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN popr_hrapp.employee_code
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN exp_hrapp.employee_code
						ELSE NULL::character varying
					END AS employee_approve,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN ((((COALESCE(pr_hrapp.title_th, ''::text) || ' '::text) || pr_hrapp.first_name_th) || ' '::text) || pr_hrapp.last_name_th)
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN ((((COALESCE(popr_hrapp.title_th, ''::text) || ' '::text) || popr_hrapp.first_name_th) || ' '::text) || popr_hrapp.last_name_th)
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN ((((COALESCE(exp_hrapp.title_th, ''::text) || ' '::text) || exp_hrapp.first_name_th) || ' '::text) || exp_hrapp.last_name_th)
						ELSE NULL::text
					END AS employee_approve_name,
				aa.amount,
					CASE
						WHEN ((aa.doctype)::text = 'purchase_request'::text) THEN (pr.date_start)::timestamp without time zone
						WHEN ((aa.doctype)::text = 'purchase_order'::text) THEN po.date_order
						WHEN ((aa.doctype)::text = 'employee_expense'::text) THEN (exp.date)::timestamp without time zone
						ELSE NULL::timestamp without time zone
					END AS date_doc,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.code
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.code
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN prj.project_code
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN sec2.section_code
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.code
						ELSE ''::character varying
					END AS source_budget_code,
					CASE
						WHEN ((aa.chart_view)::text = 'invest_construction'::text) THEN bgcon.phase_name
						WHEN ((aa.chart_view)::text = 'invest_asset'::text) THEN bgasset.name
						WHEN ((aa.chart_view)::text = 'project_base'::text) THEN (prj.project_name)::character varying
						WHEN ((aa.chart_view)::text = 'unit_base'::text) THEN (sec2.section_name)::character varying
						WHEN ((aa.chart_view)::text = 'personnel'::text) THEN budper.name
						ELSE ''::character varying
					END AS source_budget_name,
				job.code AS job_order,
				job.name AS job_order_name,
				jobtype.code AS job_order_type,
				jobtype.name AS job_order_type_name
			   FROM ((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((issi_budget_summary_consume_view aa
				 LEFT JOIN account_period perd ON ((aa.period_id = perd.id)))
				 LEFT JOIN account_fiscalyear fisyear ON ((aa.fiscalyear_id = fisyear.id)))
				 LEFT JOIN account_activity_group ag ON ((aa.activity_group_id = ag.id)))
				 LEFT JOIN account_activity a ON ((aa.activity_id = a.id)))
				 LEFT JOIN account_activity a_rpt ON ((aa.activity_rpt_id = a_rpt.id)))
				 LEFT JOIN account_account acct ON ((aa.account_id = acct.id)))
				 LEFT JOIN account_account acct_rpt ON ((a_rpt.account_id = acct_rpt.id)))
				 LEFT JOIN res_mission miss ON ((aa.mission_id = miss.id)))
				 LEFT JOIN res_org org ON ((aa.org_id = org.id)))
				 LEFT JOIN etl_issi_m_section sec2 ON ((aa.section_id = sec2.section_id)))
				 LEFT JOIN res_section res_sec ON ((aa.section_id = res_sec.id)))
				 LEFT JOIN res_section_program ressecpg ON ((res_sec.section_program_id = ressecpg.id)))
				 LEFT JOIN res_section_program secpg ON ((aa.section_program_id = secpg.id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((aa.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN etl_issi_m_project prj ON ((aa.project_id = prj.pb2_project_id)))
				 LEFT JOIN etl_issi_m_section prjsec ON ((prj.pm_section_id = prjsec.section_id)))
				 LEFT JOIN res_project res_prj ON ((aa.project_id = res_prj.id)))
				 LEFT JOIN res_program prjpg ON ((res_prj.program_id = prjpg.id)))
				 LEFT JOIN res_section_program prjsecpg ON ((prjpg.section_program_id = prjsecpg.id)))
				 LEFT JOIN issi_m_investment_construction_phase_view bgcon ON ((aa.invest_construction_phase_id = bgcon.invest_construction_phase_id)))
				 LEFT JOIN etl_issi_m_section prjcsec ON ((bgcon.pm_section_id = prjcsec.section_id)))
				 LEFT JOIN res_invest_asset bgasset ON ((aa.invest_asset_id = bgasset.id)))
				 LEFT JOIN etl_issi_m_section invasset_sec ON ((bgasset.owner_section_id = invasset_sec.section_id)))
				 LEFT JOIN res_personnel_costcenter budper ON ((aa.personnel_costcenter_id = budper.id)))
				 LEFT JOIN issi_m_personel_costcenter_view persec ON ((budper.id = persec.id)))
				 LEFT JOIN purchase_request_line pr_line ON ((aa.purchase_request_line_id = pr_line.id)))
				 LEFT JOIN purchase_request pr ON ((pr_line.request_id = pr.id)))
				 LEFT JOIN product_product pr_prod ON ((pr_line.product_id = pr_prod.id)))
				 LEFT JOIN product_template pr_prod_tm ON ((pr_prod.product_tmpl_id = pr_prod_tm.id)))
				 LEFT JOIN product_category pr_prodcat ON ((pr_prod_tm.categ_id = pr_prodcat.id)))
				 LEFT JOIN res_users pr_usreq ON ((pr.requested_by = pr_usreq.id)))
				 LEFT JOIN issi_hr_employee_view pr_hrreq ON (((pr_usreq.login)::text = (pr_hrreq.employee_code)::text)))
				 LEFT JOIN res_users pr_usrapp ON ((pr.assigned_to = pr_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view pr_hrapp ON (((pr_usrapp.login)::text = (pr_hrapp.employee_code)::text)))
				 LEFT JOIN purchase_order_line po_line ON ((aa.purchase_line_id = po_line.id)))
				 LEFT JOIN purchase_order po ON ((po_line.order_id = po.id)))
				 LEFT JOIN purchase_request_purchase_order_line_rel prpo_rel ON ((po_line.id = prpo_rel.purchase_order_line_id)))
				 LEFT JOIN purchase_request_line popr_line ON ((prpo_rel.purchase_request_line_id = popr_line.id)))
				 LEFT JOIN purchase_request popr ON ((popr_line.request_id = popr.id)))
				 LEFT JOIN purchase_order po_rfq ON ((po.quote_id = po_rfq.id)))
				 LEFT JOIN purchase_requisition poreq ON ((po_rfq.requisition_id = poreq.id)))
				 LEFT JOIN purchase_method pometh ON ((poreq.purchase_method_id = pometh.id)))
				 LEFT JOIN purchase_contract po_con ON ((po.contract_id = po_con.id)))
				 LEFT JOIN product_product po_prod ON ((po_line.product_id = po_prod.id)))
				 LEFT JOIN product_template po_prod_tm ON ((po_prod.product_tmpl_id = po_prod_tm.id)))
				 LEFT JOIN product_category po_prodcat ON ((po_prod_tm.categ_id = po_prodcat.id)))
				 LEFT JOIN res_partner po_partner ON ((po.partner_id = po_partner.id)))
				 LEFT JOIN res_users popr_usreq ON ((popr.requested_by = popr_usreq.id)))
				 LEFT JOIN issi_hr_employee_view popr_hrreq ON (((popr_usreq.login)::text = (popr_hrreq.employee_code)::text)))
				 LEFT JOIN res_users popr_usrapp ON ((popr.assigned_to = popr_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view popr_hrapp ON (((popr_usrapp.login)::text = (popr_hrapp.employee_code)::text)))
				 LEFT JOIN hr_expense_line exp_line ON ((aa.expense_line_id = exp_line.id)))
				 LEFT JOIN hr_expense_expense exp ON ((exp_line.expense_id = exp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrreq ON ((exp.employee_id = exp_hrreq.id)))
				 LEFT JOIN res_users exp_usrapp ON ((exp.approver_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrapp ON (((exp_usrapp.login)::text = (exp_hrapp.employee_code)::text)))
				 LEFT JOIN res_users exp_usrpre ON ((exp.user_id = exp_usrpre.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrpre ON (((exp_usrpre.login)::text = (exp_hrpre.employee_code)::text)))
				 LEFT JOIN cost_control job ON ((aa.cost_control_id = job.id)))
				 LEFT JOIN cost_control_type jobtype ON ((aa.cost_control_type_id = jobtype.id)))
			  WHERE (((aa.budget_commit_type)::text <> 'actual'::text) AND (aa.amount <> (0)::numeric))
        )
        """ % self._table)
