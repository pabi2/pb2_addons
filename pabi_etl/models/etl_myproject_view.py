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

class ISSIMSourceBudget(models.Model):
    _name = 'issi.m.source.budget.view'
    _auto = False
    _description = 'HR employee view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as ( 
			SELECT 'project_base'::text AS budget_view,
				p.pb2_project_id AS project_id,
				NULL::integer AS section_id,
				NULL::integer AS invest_construction_phase_id,
				NULL::integer AS invest_asset_id,
				NULL::integer AS personnel_costcenter_id,
				p.project_code AS source_budget,
				p.project_name AS source_budget_name,
				p.org_code,
				p.org_name_short_en AS org_name,
				p.mission,
				p.pm_code AS pm,
				p.pm_name,
				p.costcenter_code AS costcenter_used,
				p.costcenter_name AS costcenter_name_used,
				p.pm_section_code AS section_code,
				p.pm_section_name AS section_name,
				psec.division_code AS division,
				psec.division_name,
				psec.subsector_code AS sub_sector,
				psec.subsector_name AS sub_sector_name,
				psec.sector_code AS sector,
				psec.sector_name,
				psecprg.code AS section_program,
				psecprg.name AS section_program_name,
				p.functional_area_code AS functional_area,
				p.functional_area_name,
				p.program_group_code AS program_group,
				p.program_group_name,
				p.program_code AS program,
				p.program_name,
				p.project_group_code AS project_group,
				p.project_group_name,
				p.reference_program_code AS reference_program,
				p.reference_program_name,
				p.current_program_code AS current_program,
				p.current_program_name,
				p.master_plan_code AS master_plan,
				p.master_plan_name,
				p.project_type_code AS project_type,
				p.project_type_name,
				p.operation_code,
				p.operation_name,
				p.fund_code AS fund_type_code,
				p.fund_name AS fund_type_name,
				array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
					   FROM (res_fund_project_rel a
						 LEFT JOIN res_fund b ON ((a.fund_id = b.id)))
					  WHERE (a.project_id = p.pb2_project_id)), ', '::text) AS source_of_fund,
				p.date_approve AS project_approve_date,
				p.project_date_start,
				p.project_date_end,
				p.contract_date_start,
				p.contract_date_end,
				p.date_start,
				p.date_end,
				p.project_date_end_proposal,
				NULL::text AS phase_date_expansion,
				p.project_date_terminate,
				p.project_date_close,
				p.project_date_close_cond,
				p.pb2_status AS project_status,
				p.myp_status,
				NULL::character varying AS project_c_code,
				NULL::character varying AS project_c_name,
				NULL::date AS project_c_date_start,
				NULL::date AS project_c_date_end,
				NULL::date AS project_c_date_expansion,
				NULL::character varying AS project_c_status,
				pprj.active,
				pprj.proposal_overall_budget AS plan_proposal_overall_expense,
				pprj.overall_expense_budget AS plan_overall_external,
				pprj.overall_expense_budget_internal AS plan_overall_expense_internal,
				pprj.overall_revenue_plan AS plan_overall_revenue_external,
				p.pb2_costcenter_id AS costcenter_id
			   FROM ((((etl_issi_m_project p
				 LEFT JOIN etl_issi_m_section psec ON ((p.pm_section_id = psec.section_id)))
				 LEFT JOIN res_project pprj ON ((p.pb2_project_id = pprj.id)))
				 LEFT JOIN res_program pprg ON ((p.pb2_program_id = pprg.id)))
				 LEFT JOIN res_section_program psecprg ON ((pprg.section_program_id = psecprg.id)))
			UNION
			 SELECT 'invest_construction'::text AS budget_view,
				NULL::integer AS project_id,
				NULL::integer AS section_id,
				c.invest_construction_phase_id,
				NULL::integer AS invest_asset_id,
				NULL::integer AS personnel_costcenter_id,
				c.code AS source_budget,
				c.phase_name AS source_budget_name,
				c.org_code,
				c.org_name_short AS org_name,
				c.mission,
				c.pm_code AS pm,
				c.pm_name,
				c.costcenter_code AS costcenter_used,
				c.costcenter_name AS costcenter_name_used,
				c.pm_section_code AS section_code,
				c.pm_section_name AS section_name,
				sec.division_code AS division,
				sec.division_name,
				sec.subsector_code AS sub_sector,
				sec.subsector_name AS sub_sector_name,
				sec.sector_code AS sector,
				sec.sector_name,
				secprg.code AS section_program,
				secprg.name AS section_program_name,
				NULL::character varying AS functional_area,
				NULL::text AS functional_area_name,
				NULL::character varying AS program_group,
				NULL::text AS program_group_name,
				NULL::character varying AS program,
				NULL::text AS program_name,
				NULL::character varying AS project_group,
				NULL::text AS project_group_name,
				NULL::character varying AS reference_program,
				NULL::text AS reference_program_name,
				NULL::character varying AS current_program,
				NULL::text AS current_program_name,
				NULL::character varying AS master_plan,
				NULL::character varying AS master_plan_name,
				NULL::character varying AS project_type,
				NULL::character varying AS project_type_name,
				NULL::character varying AS operation_code,
				NULL::character varying AS operation_name,
				c.phase_fund_type_code AS fund_type_code,
				c.phase_fund_type AS fund_type_name,
				array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
					   FROM (res_fund_invest_construction_phase_rel a
						 LEFT JOIN res_fund b ON ((a.fund_id = b.id)))
					  WHERE (a.invest_construction_phase_id = c.invest_construction_phase_id)), ', '::text) AS source_of_fund,
				NULL::date AS project_approve_date,
				c.phase_date_start AS project_date_start,
				c.phase_contract_date_end AS project_date_end,
				c.phase_contract_date_start AS contract_date_start,
				c.phase_contract_date_end AS contract_date_end,
				c.phase_date_start AS date_start,
					CASE
						WHEN (c.phase_date_expansion IS NOT NULL) THEN c.phase_date_expansion
						ELSE c.phase_date_end
					END AS date_end,
				NULL::date AS project_date_end_proposal,
				NULL::text AS phase_date_expansion,
				NULL::date AS project_date_terminate,
					CASE
						WHEN (((c.phase_state)::text = 'close'::text) AND (c.phase_date_expansion IS NOT NULL)) THEN c.phase_date_expansion
						WHEN (((c.phase_state)::text = 'close'::text) AND (c.phase_date_expansion IS NULL)) THEN c.phase_date_end
						ELSE NULL::date
					END AS project_date_close,
				NULL::date AS project_date_close_cond,
				c.phase_state AS project_status,
				NULL::character varying AS myp_status,
				c.construction_code AS project_c_code,
				c.construction_name AS project_c_name,
				c.date_start AS project_c_date_start,
				c.date_end AS project_c_date_end,
				c.date_expansion AS project_c_date_expansion,
				c.state AS project_c_status,
				c.active,
				COALESCE(( SELECT sum(b.amount_plan_init) AS sum
					   FROM res_invest_construction_phase_plan b
					  WHERE (b.invest_construction_phase_id = c.invest_construction_phase_id)
					  GROUP BY b.invest_construction_phase_id), (0)::double precision) AS plan_proposal_overall_expense,
				COALESCE(( SELECT sum(b.amount_plan) AS sum
					   FROM res_invest_construction_phase_plan b
					  WHERE (b.invest_construction_phase_id = c.invest_construction_phase_id)
					  GROUP BY b.invest_construction_phase_id), (0)::double precision) AS plan_overall_external,
				0.00 AS plan_overall_expense_internal,
				0.00 AS plan_overall_revenue_external,
				c.costcenter_id
			   FROM (((issi_m_investment_construction_phase_view c
				 LEFT JOIN etl_issi_m_section sec ON ((c.pm_section_id = sec.section_id)))
				 LEFT JOIN res_section ressec ON ((sec.section_id = ressec.id)))
				 LEFT JOIN res_program secprg ON ((ressec.section_program_id = secprg.id)))
			UNION
			 SELECT 'invest_asset'::text AS budget_view,
				NULL::integer AS project_id,
				NULL::integer AS section_id,
				NULL::integer AS invest_construction_phase_id,
				a.investment_asset_id AS invest_asset_id,
				NULL::integer AS personnel_costcenter_id,
				a.invest_asset_code AS source_budget,
				a.invest_asset_name AS source_budget_name,
				a.org_code,
				a.org_name,
				a.mission,
				NULL::character varying AS pm,
				NULL::text AS pm_name,
				a.costcenter_code AS costcenter_used,
				a.costcenter_name AS costcenter_name_used,
				a.section_code,
				a.section_name,
				a.division_code AS division,
				a.division_name,
				a.subsector_code AS sub_sector,
				a.subsector_name AS sub_sector_name,
				a.sector_code AS sector,
				a.sector_name,
				a.section_program,
				a.section_program_name,
				a.functional_area,
				a.functional_area_name,
				a.program_group,
				a.program_group_name,
				a.program_code AS program,
				a.program_name,
				NULL::character varying AS project_group,
				NULL::text AS project_group_name,
				NULL::character varying AS reference_program,
				NULL::text AS reference_program_name,
				NULL::character varying AS current_program,
				NULL::text AS current_program_name,
				NULL::character varying AS master_plan,
				NULL::character varying AS master_plan_name,
				NULL::character varying AS project_type,
				NULL::character varying AS project_type_name,
				NULL::character varying AS operation_code,
				NULL::character varying AS operation_name,
				NULL::character varying AS fund_type_code,
				NULL::character varying AS fund_type_name,
				array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
					   FROM (res_fund_invest_asset_rel aa
						 LEFT JOIN res_fund b ON ((aa.fund_id = b.id)))
					  WHERE (aa.invest_asset_id = a.investment_asset_id)), ', '::text) AS source_of_fund,
				NULL::date AS project_approve_date,
				NULL::date AS project_date_start,
				NULL::date AS project_date_end,
				NULL::date AS contract_date_start,
				NULL::date AS contract_date_end,
				NULL::date AS date_start,
				NULL::date AS date_end,
				NULL::date AS project_date_end_proposal,
				NULL::text AS phase_date_expansion,
				NULL::date AS project_date_terminate,
				NULL::date AS project_date_close,
				NULL::date AS project_date_close_cond,
				NULL::character varying AS project_status,
				NULL::character varying AS myp_status,
				NULL::character varying AS project_c_code,
				NULL::character varying AS project_c_name,
				NULL::date AS project_c_date_start,
				NULL::date AS project_c_date_end,
				NULL::date AS project_c_date_expansion,
				NULL::character varying AS project_c_status,
				a.active,
				0.00 AS plan_proposal_overall_expense,
				0.00 AS plan_overall_external,
				0.00 AS plan_overall_expense_internal,
				0.00 AS plan_overall_revenue_external,
				a.costcenter_id
			   FROM issi_m_investment_asset_view a
			UNION
			 SELECT 'unit_base'::text AS budget_view,
				NULL::integer AS project_id,
				s.section_id,
				NULL::integer AS invest_construction_phase_id,
				NULL::integer AS invest_asset_id,
				NULL::integer AS personnel_costcenter_id,
				s.section_code AS source_budget,
				s.section_name AS source_budget_name,
				s.org_code,
				s.org_name_short_en AS org_name,
				s.mission_code AS mission,
				NULL::character varying AS pm,
				NULL::text AS pm_name,
				s.costcenter_code AS costcenter_used,
				s.costcenter_name AS costcenter_name_used,
				s.section_code,
				s.section_name,
				s.division_code AS division,
				s.division_name,
				s.subsector_code AS sub_sector,
				s.subsector_name AS sub_sector_name,
				s.sector_code AS sector,
				s.sector_name,
				secprg.code AS section_program,
				secprg.name AS section_program_name,
				NULL::character varying AS functional_area,
				NULL::text AS functional_area_name,
				NULL::character varying AS program_group,
				NULL::text AS program_group_name,
				NULL::character varying AS program,
				NULL::text AS program_name,
				NULL::character varying AS project_group,
				NULL::text AS project_group_name,
				NULL::character varying AS reference_program,
				NULL::text AS reference_program_name,
				NULL::character varying AS current_program,
				NULL::text AS current_program_name,
				NULL::character varying AS master_plan,
				NULL::character varying AS master_plan_name,
				NULL::character varying AS project_type,
				NULL::character varying AS project_type_name,
				NULL::character varying AS operation_code,
				NULL::character varying AS operation_name,
				NULL::character varying AS fund_type_code,
				NULL::character varying AS fund_type_name,
				array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
					   FROM (res_fund_section_rel a
						 LEFT JOIN res_fund b ON ((a.fund_id = b.id)))
					  WHERE (a.section_id = s.section_id)), ', '::text) AS source_of_fund,
				NULL::date AS project_approve_date,
				NULL::date AS project_date_start,
				NULL::date AS project_date_end,
				NULL::date AS contract_date_start,
				NULL::date AS contract_date_end,
				NULL::date AS date_start,
				NULL::date AS date_end,
				NULL::date AS project_date_end_proposal,
				NULL::text AS phase_date_expansion,
				NULL::date AS project_date_terminate,
				NULL::date AS project_date_close,
				NULL::date AS project_date_close_cond,
				NULL::character varying AS project_status,
				NULL::character varying AS myp_status,
				NULL::character varying AS project_c_code,
				NULL::character varying AS project_c_name,
				NULL::date AS project_c_date_start,
				NULL::date AS project_c_date_end,
				NULL::date AS project_c_date_expansion,
				NULL::character varying AS project_c_status,
				ssec.active,
				0.00 AS plan_proposal_overall_expense,
				0.00 AS plan_overall_external,
				0.00 AS plan_overall_expense_internal,
				0.00 AS plan_overall_revenue_external,
				s.costcenter_id
			   FROM ((etl_issi_m_section s
				 LEFT JOIN res_section ssec ON ((s.section_id = ssec.id)))
				 LEFT JOIN res_program secprg ON ((ssec.section_program_id = secprg.id)))
			  WHERE (s.section_id <> ALL (ARRAY[142, 134, 9999999, 23, 446, 448]))
			UNION
			 SELECT 'personnel'::text AS budget_view,
				NULL::integer AS project_id,
				NULL::integer AS section_id,
				NULL::integer AS invest_construction_phase_id,
				NULL::integer AS invest_asset_id,
				p.id AS personnel_costcenter_id,
				p.code AS source_budget,
				p.name AS source_budget_name,
				p.org_code,
				p.org_name_short_en AS org_name,
				'IM'::character varying AS mission,
				NULL::character varying AS pm,
				NULL::text AS pm_name,
				p.costcenter_code AS costcenter_used,
				p.costcenter_name AS costcenter_name_used,
				NULL::character varying AS section_code,
				NULL::text AS section_name,
				p.division_code AS division,
				p.division_name,
				p.subsector_code AS sub_sector,
				p.subsector_name AS sub_sector_name,
				p.sector_code AS sector,
				p.sector_name,
				NULL::character varying AS section_program,
				NULL::character varying AS section_program_name,
				NULL::character varying AS functional_area,
				NULL::text AS functional_area_name,
				NULL::character varying AS program_group,
				NULL::text AS program_group_name,
				NULL::character varying AS program,
				NULL::text AS program_name,
				NULL::character varying AS project_group,
				NULL::text AS project_group_name,
				NULL::character varying AS reference_program,
				NULL::text AS reference_program_name,
				NULL::character varying AS current_program,
				NULL::text AS current_program_name,
				NULL::character varying AS master_plan,
				NULL::character varying AS master_plan_name,
				NULL::character varying AS project_type,
				NULL::character varying AS project_type_name,
				NULL::character varying AS operation_code,
				NULL::character varying AS operation_name,
				NULL::character varying AS fund_type_code,
				NULL::character varying AS fund_type_name,
				array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
					   FROM (res_fund_personnel_costcenter_rel a
						 LEFT JOIN res_fund b ON ((a.fund_id = b.id)))
					  WHERE (a.personnel_costcenter_id = p.id)), ', '::text) AS source_of_fund,
				NULL::date AS project_approve_date,
				NULL::date AS project_date_start,
				NULL::date AS project_date_end,
				NULL::date AS contract_date_start,
				NULL::date AS contract_date_end,
				NULL::date AS date_start,
				NULL::date AS date_end,
				NULL::date AS project_date_end_proposal,
				NULL::text AS phase_date_expansion,
				NULL::date AS project_date_terminate,
				NULL::date AS project_date_close,
				NULL::date AS project_date_close_cond,
				NULL::character varying AS project_status,
				NULL::character varying AS myp_status,
				NULL::character varying AS project_c_code,
				NULL::character varying AS project_c_name,
				NULL::date AS project_c_date_start,
				NULL::date AS project_c_date_end,
				NULL::date AS project_c_date_expansion,
				NULL::character varying AS project_c_status,
				per.active,
				0.00 AS plan_proposal_overall_expense,
				0.00 AS plan_overall_external,
				0.00 AS plan_overall_expense_internal,
				0.00 AS plan_overall_revenue_external,
				p.costcenter_id
			   FROM (issi_m_personel_costcenter_view p
				 LEFT JOIN res_personnel_costcenter per ON ((p.id = per.id)))
		)
    """ % self._table)
