# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools

class issi_hr_employee_view(models.Model):
    _name = 'issi.hr.employee.view'
    _auto = False
    _description = 'HR employee view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
             SELECT e.id,
                e.employee_code,
                e.first_name,
                t.name AS title,
                e.last_name,
                e.work_phone,
                e.mobile_phone,
                o.name AS org_desc,
                s.id AS section_id,
                concat('[', btrim((s.code)::text), '] ', s.name) AS section_desc,
                d.name AS div_name,
                COALESCE(irt.value, (t.name)::text) AS title_th,
                COALESCE(irf.value, (e.first_name)::text) AS first_name_th,
                COALESCE(irl.value, (e.last_name)::text) AS last_name_th,
                COALESCE(iro.value, (o.name)::text) AS org_desc_th,
                concat('[', btrim((s.code)::text), '] ', COALESCE(irs.value, (s.name)::text)) AS section_desc_th,
                COALESCE(ird.value, (d.name)::text) AS div_name_th,
                po.name AS "position",
                COALESCE(irp.value, (po.name)::text) AS position_th,
                e.org_id,
                u.active,
                ((((COALESCE(irt.value, COALESCE((t.name)::text, ''::text)) || ' '::text) || COALESCE(irf.value, (e.first_name)::text)) || ' '::text) || COALESCE(irl.value, (e.last_name)::text)) AS full_name_th,
                (((((COALESCE(t.name, ''::character varying))::text || ' '::text) || (COALESCE(e.first_name, ''::character varying))::text) || ' '::text) || (COALESCE(e.last_name, ''::character varying))::text) AS full_name_en,
                ((((((('['::text || (e.employee_code)::text) || '] '::text) || COALESCE(irt.value, COALESCE((t.name)::text, ''::text))) || ' '::text) || COALESCE(irf.value, (e.first_name)::text)) || ' '::text) || COALESCE(irl.value, (e.last_name)::text)) AS display_name_th,
                ((((((('['::text || (e.employee_code)::text) || '] '::text) || (COALESCE(t.name, ''::character varying))::text) || ' '::text) || (COALESCE(e.first_name, ''::character varying))::text) || ' '::text) || (COALESCE(e.last_name, ''::character varying))::text) AS display_name_en
               FROM (((((((((((((hr_employee e
                 JOIN res_users u ON (((e.employee_code)::text = (u.login)::text)))
                 LEFT JOIN res_org o ON ((e.org_id = o.id)))
                 LEFT JOIN hr_position po ON ((e.position_id = po.id)))
                 LEFT JOIN res_partner_title t ON ((e.title_id = t.id)))
                 LEFT JOIN res_section s ON ((e.section_id = s.id)))
                 LEFT JOIN res_division d ON ((d.id = s.division_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.partner.title,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irt ON ((t.id = irt.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'hr.employee,first_name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irf ON ((e.id = irf.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'hr.employee,last_name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irl ON ((e.id = irl.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.org,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) iro ON ((o.id = iro.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.section,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irs ON ((s.id = irs.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'res.division,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) ird ON ((d.id = ird.res_id)))
                 LEFT JOIN ( SELECT ir_translation.res_id,
                        ir_translation.value
                       FROM ir_translation
                      WHERE (((ir_translation.name)::text = 'hr.position,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irp ON ((po.id = irp.res_id)))
        )
        """ % self._table)
	
class etl_issi_m_section(models.Model):
    _name = 'etl.issi.m.project'
    _auto = False
    _description = 'ETL Master Project'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
		CREATE or REPLACE VIEW %s as ( 
		SELECT s.id AS section_id,
			s.code AS section_code,
			COALESCE(irs.value, (s.name)::text) AS section_name,
			(s.name)::text AS section_name_en,
			o.id AS org_id,
			o.code AS org_code,
			COALESCE(iro.value, (o.name)::text) AS org_name,
			o.name AS org_name_en,
			COALESCE(iro_short.value, (o.name_short)::text) AS org_name_short,
			o.name_short AS org_name_short_en,
			sc.id AS sector_id,
			sc.code AS sector_code,
			COALESCE(irsc.value, (sc.name)::text) AS sector_name,
			COALESCE(irsc_short.value, (sc.name_short)::text) AS sector_name_short,
			(sc.name)::text AS sector_name_en,
			(sc.name_short)::text AS sector_name_short_en,
			sb.id AS subsector_id,
			sb.code AS subsector_code,
			COALESCE(irsb.value, (sb.name)::text) AS subsector_name,
			COALESCE(irsb_short.value, (sb.name_short)::text) AS subsector_name_short,
			(sb.name)::text AS subsector_name_en,
			(sb.name_short)::text AS subsector_name_short_en,
			d.id AS division_id,
			d.code AS division_code,
			COALESCE(ird.value, (d.name)::text) AS division_name,
			COALESCE(ird_short.value, (d.name_short)::text) AS division_name_short,
			(d.name)::text AS division_name_en,
			(d.name_short)::text AS division_name_short_en,
			c.id AS costcenter_id,
			c.code AS costcenter_code,
			COALESCE(irc.value, (c.name)::text) AS costcenter_name,
			COALESCE(irc_short.value, (c.name_short)::text) AS costcenter_name_short,
			(c.name)::text AS costcenter_name_en,
			(c.name_short)::text AS costcenter_name_short_en,
			s.name_short AS section_name_short,
			s.internal_charge,
			(miss.name)::text AS mission_code,
			s.name_short AS section_name_short_en,
			s.create_date,
			s.write_date,
			s.active AS section_active,
			c.active AS costcenter_active,
			s.ehr_id
		   FROM (((((((((((((((((res_section s
			 LEFT JOIN res_org o ON ((s.org_id = o.id)))
			 LEFT JOIN res_sector sc ON ((s.sector_id = sc.id)))
			 LEFT JOIN res_subsector sb ON ((s.subsector_id = sb.id)))
			 LEFT JOIN res_division d ON ((s.division_id = d.id)))
			 LEFT JOIN res_costcenter c ON ((s.costcenter_id = c.id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.section,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irs ON ((s.id = irs.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.org,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) iro ON ((s.org_id = iro.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) iro_short ON ((s.org_id = iro_short.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.costcenter,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irc ON ((s.costcenter_id = irc.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.costcenter,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irc_short ON ((s.costcenter_id = irc_short.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.sector,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsc ON ((s.sector_id = irsc.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.sector,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsc_short ON ((s.sector_id = irsc_short.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.subsector,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsb ON ((s.subsector_id = irsb.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.subsector,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsb_short ON ((s.subsector_id = irsb_short.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.division,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) ird ON ((s.division_id = ird.res_id)))
			 LEFT JOIN ( SELECT ir_translation.res_id,
					ir_translation.value
				   FROM ir_translation
				  WHERE (((ir_translation.name)::text = 'res.division,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) ird_short ON ((s.division_id = ird_short.res_id)))
			 LEFT JOIN res_mission miss ON ((miss.id = s.mission_id)))
		  ORDER BY s.code
		)
    """ % self._table)	
		
class etl_issi_m_project(models.Model):
    _name = 'etl.issi.m.project'
    _auto = False
    _description = 'ETL Master Project'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (  
			SELECT src.id AS pb2_project_id,
			src.code AS project_code,
			src.name_th AS project_name,
			src.name AS project_name_en,
			miss.name AS mission,
			org.id AS pb2_org_id,
			org.code AS org_code,
			src.org_name_th AS org_name,
			src.org_name AS org_name_en,
			src.org_name_short_th AS org_name_short,
			src.org_name_short AS org_name_short_en,
			src.functional_area_id AS pb2_functional_area_id,
			src.functional_area_code,
			src.functional_area_name,
			src.functional_area_name_en,
			src.program_group_id AS pb2_program_group_id,
			src.program_group_code,
			src.program_group_name,
			src.program_group_name_en,
			src.program_id AS pb2_program_id,
			src.program_code,
			src.program_name,
			src.program_name_en,
			src.project_group_id AS pb2_project_group_id,
			src.project_group_code,
			src.project_group_name,
			src.project_group_name_en,
			src.costcenter_id AS pb2_costcenter_id,
			src.costcenter_code,
			src.costcenter_name,
			src.costcenter_name_en,
			subpg.code AS subprogram_code,
			subpg.name AS subprogram_name,
			refpg.code AS reference_program_code,
			refpg.name AS reference_program_name,
			curpg.code AS current_program_code,
			curpg.name AS current_program_name,
			nt_strategy_group.code AS nstda_strategy_group_code,
			nt_strategy_group.name AS nstda_strategy_group_name,
			nt_strategy.code AS nstda_strategy_code,
			nt_strategy.name AS nstda_strategy_name,
			pjt.code AS project_type_code,
			pjt.name AS project_type_name,
			prj.project_kind,
			oper.code AS operation_code,
			oper.name AS operation_name,
			fund.code AS fund_code,
			fund.name AS fund_name,
			prj.external_fund_type,
			prj.external_fund_name,
			mtp.code AS master_plan_code,
			mtp.name AS master_plan_name,
			src.pm_code,
			src.pm_name_th AS pm_name,
			src.pm_name AS pm_name_en,
			prj.external_pm AS external_pm_name,
			prj.date_start,
			prj.date_approve,
			prj.date_end,
			prj.contract_date_start AS date_contract_start,
			prj.contract_date_end AS date_contract_end,
				CASE
					WHEN (prj.conversion_project IS TRUE) THEN 1
					ELSE 0
				END AS is_conversion,
			src.state AS pb2_status,
			myp.name AS myp_status,
			pmsec.section_code AS pm_section_code,
			pmsec.section_name AS pm_section_name,
			prj.project_date_start,
			prj.project_date_end,
			prj.project_date_end_proposal,
			prj.project_date_close,
			prj.project_date_close_cond,
			prj.project_date_terminate,
			pmsec.section_id AS pm_section_id,
			prj.contract_date_start,
			prj.contract_date_end,
			analyst.employee_code AS analyst_code,
			((((COALESCE(analyst.title_th, ''::text) || ' '::text) || COALESCE(analyst.first_name_th, ''::text)) || ' '::text) || COALESCE(analyst.last_name_th, ''::text)) AS analyst_name,
			array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
				   FROM (res_fund_project_rel a
					 LEFT JOIN res_fund b ON ((a.fund_id = b.id)))
				  WHERE (a.project_id = prj.id)), ', '::text) AS source_of_fund,
			prj.proposal_program_id AS current_program_id
		   FROM ((((((((((((((((issi_selection_project_view src
			 JOIN res_project prj ON ((src.id = prj.id)))
			 JOIN res_org org ON ((prj.org_id = org.id)))
			 LEFT JOIN res_mission miss ON ((prj.mission_id = miss.id)))
			 LEFT JOIN myproject_status myp ON ((prj.project_status = myp.id)))
			 LEFT JOIN project_nstda_strategy nt_strategy ON ((prj.nstda_strategy_id = nt_strategy.id)))
			 LEFT JOIN project_nstda_strategy_group nt_strategy_group ON ((nt_strategy.group_id = nt_strategy_group.id)))
			 LEFT JOIN project_master_plan mtp ON ((prj.master_plan_id = mtp.id)))
			 LEFT JOIN project_type pjt ON ((prj.project_type_id = pjt.id)))
			 LEFT JOIN project_operation oper ON ((prj.operation_id = oper.id)))
			 LEFT JOIN project_fund_type fund ON ((prj.fund_type_id = fund.id)))
			 LEFT JOIN issi_selection_program_view subpg ON ((prj.subprogram_id = subpg.id)))
			 LEFT JOIN issi_selection_program_view refpg ON ((prj.ref_program_id = refpg.id)))
			 LEFT JOIN issi_selection_program_view curpg ON ((prj.proposal_program_id = curpg.id)))
			 LEFT JOIN hr_employee hr ON ((prj.pm_employee_id = hr.id)))
			 LEFT JOIN etl_issi_m_section pmsec ON ((hr.section_id = pmsec.section_id)))
			 LEFT JOIN issi_hr_employee_view analyst ON ((prj.analyst_employee_id = analyst.id)))
		)
    """ % self._table)

class etl_issi_m_project_c(models.Model):
    _name = 'etl.issi.m.project.c'
    _auto = False
    _description = 'ETL Master Project C'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			SELECT conphase.id AS invest_construction_phase_id,
				conphase.code AS source_budget,
				conphase.name AS source_budget_name,
				conphase.phase AS phase_name,
				org.id AS org_id,
				org.code AS org_code,
				org.name AS org_name,
				org.name_short AS org_name_short,
				mission.name AS mission,
				hr.employee_code AS pm,
				((((COALESCE(hr.title_th, ''::text) || ' '::text) || hr.first_name_th) || ' '::text) || hr.last_name_th) AS pm_name,
				cctr.costcenter_code AS costcenter_used,
				cctr.costcenter_name AS costcenter_name_used,
				cctr.costcenter_name_short AS costcenter_name_used_short,
				sec.section_code,
				sec.section_name,
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
				projfund.code AS fund_type_code,
				projfund.name AS fund_type_name,
				array_to_string(ARRAY( SELECT (((COALESCE(b.code, ''::character varying))::text || '-'::text) || (COALESCE(b.name, ''::character varying))::text)
					   FROM (res_fund_invest_construction_phase_rel a
						 LEFT JOIN res_fund b ON ((a.fund_id = b.id)))
					  WHERE (a.invest_construction_phase_id = conphase.id)), ', '::text) AS source_of_fund,
				NULL::date AS project_approve_date,
				conphase.date_start AS project_date_start,
				conphase.contract_date_end AS project_date_end,
				conphase.contract_date_start,
				conphase.contract_date_end,
				conphase.contract_day_duration,
				conphase.date_start,
				conphase.legacy_ref AS legacy_code,
					CASE
						WHEN (conphase.date_expansion IS NOT NULL) THEN conphase.date_expansion
						ELSE conphase.date_end
					END AS date_end,
				NULL::date AS project_date_end_proposal,
				NULL::text AS phase_date_expansion,
				NULL::date AS project_date_terminate,
					CASE
						WHEN (((conphase.state)::text = 'close'::text) AND (conphase.date_expansion IS NOT NULL)) THEN conphase.date_expansion
						WHEN (((conphase.state)::text = 'close'::text) AND (conphase.date_expansion IS NULL)) THEN conphase.date_end
						ELSE NULL::date
					END AS project_date_close,
				NULL::date AS project_date_close_cond,
				conphase.state AS project_status,
				conphase.month_duration,
				conphase.amount_phase_approve,
				NULL::character varying AS myp_status,
				con.code AS project_c_code,
				con.name AS project_c_name,
				con.legacy_ref AS project_c_legacy_code,
				con.date_start AS project_c_date_start,
				con.date_end AS project_c_date_end,
				con.date_expansion AS project_c_date_expansion,
				con.state AS project_c_status,
				con.active,
				COALESCE(( SELECT sum(b.amount_plan_init) AS sum
					   FROM res_invest_construction_phase_plan b
					  WHERE (b.invest_construction_phase_id = conphase.id)
					  GROUP BY b.invest_construction_phase_id), (0)::double precision) AS plan_proposal_overall_expense,
				COALESCE(( SELECT sum(b.amount_plan) AS sum
					   FROM res_invest_construction_phase_plan b
					  WHERE (b.invest_construction_phase_id = conphase.id)
					  GROUP BY b.invest_construction_phase_id), (0)::double precision) AS plan_overall_external,
				0.00 AS plan_overall_expense_internal,
				0.00 AS plan_overall_revenue_external,
				purchase.purchase_contract_id AS contract_number
			   FROM ((((((((((res_invest_construction_phase conphase
				 LEFT JOIN res_invest_construction con ON ((conphase.invest_construction_id = con.id)))
				 LEFT JOIN purchase_contract_res_invest_construction_phase_rel purchase ON ((conphase.invest_construction_id = purchase.res_invest_construction_phase_id)))
				 LEFT JOIN project_fund_type projfund ON ((conphase.fund_type_id = projfund.id)))
				 LEFT JOIN res_org org ON ((con.org_id = org.id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((con.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN issi_hr_employee_view hr ON ((con.pm_employee_id = hr.id)))
				 LEFT JOIN etl_issi_m_section sec ON ((con.pm_section_id = sec.section_id)))
				 LEFT JOIN res_section ressec ON ((sec.section_id = ressec.id)))
				 LEFT JOIN res_program secprg ON ((ressec.section_program_id = secprg.id)))
				 LEFT JOIN res_mission mission ON ((con.mission_id = mission.id)))
			  ORDER BY conphase.code, conphase.sequence
		)
    """ % self._table)

class issi_m_investment_construction_phase_view(models.Model):
    _name = 'issi.m.investment.construction.phase.view'
    _auto = False
    _description = 'ETL Master Project C Phase'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (  
			SELECT conphase.invest_construction_id,
			con.code AS construction_code,
			con.name AS construction_name,
			con.name_short AS construction_name_short,
			org.id AS org_id,
			org.code AS org_code,
			org.name_short AS org_name_short,
			org.name AS org_name,
			mission.name AS mission,
			cctr.costcenter_code,
			cctr.costcenter_name,
			hr.employee_code AS pm_code,
			((((COALESCE(hr.title_th, ''::text) || ' '::text) || hr.first_name_th) || ' '::text) || hr.last_name_th) AS pm_name,
			sec.section_id AS pm_section_id,
			sec.section_code AS pm_section_code,
			sec.section_name AS pm_section_name,
			con.date_start,
			con.date_end,
			con.date_expansion,
			con.state,
			con.active,
			con.special,
			con.approval_info,
			con.operation_area,
			con.reason,
			con.project_readiness,
			con.legacy_ref,
			conphase.id AS invest_construction_phase_id,
			conphase.code,
			conphase.name AS phase_name,
			conphase.name_short AS phase_name_short,
			conphase.sequence AS phase_sequence,
			conphase.phase,
			fund.name AS phase_fund_type,
			COALESCE(conphase.amount_phase_approve, (0)::double precision) AS amount_phase_approve,
			conphase.date_start AS phase_date_start,
			conphase.date_end AS phase_date_end,
			conphase.contract_date_start AS phase_contract_date_start,
			conphase.contract_date_end AS phase_contract_date_end,
			conphase.date_expansion AS phase_date_expansion,
			conphase.active AS phase_active,
			conphase.state AS phase_state,
			conphase.special AS phase_special,
			conphase.legacy_ref AS phase_legacy_ref,
			fund.code AS phase_fund_type_code,
			cctr.costcenter_id
		   FROM (((((((res_invest_construction_phase conphase
			 LEFT JOIN res_invest_construction con ON ((conphase.invest_construction_id = con.id)))
			 LEFT JOIN res_org org ON ((con.org_id = org.id)))
			 LEFT JOIN project_fund_type fund ON ((conphase.fund_type_id = fund.id)))
			 LEFT JOIN etl_issi_m_costcenter cctr ON ((con.costcenter_id = cctr.costcenter_id)))
			 LEFT JOIN issi_hr_employee_view hr ON ((con.pm_employee_id = hr.id)))
			 LEFT JOIN etl_issi_m_section sec ON ((con.pm_section_id = sec.section_id)))
			 LEFT JOIN res_mission mission ON ((con.mission_id = mission.id)))
		  ORDER BY conphase.code, conphase.sequence
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

class issi_m_investment_asset_view(models.Model):
    _name = 'issi.m.investment.asset.view'
    _auto = False
    _description = 'issi_m_investment_asset_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (  
			 SELECT a.id AS investment_asset_id,
				fis.name AS fiscal_year,
				a.code AS invest_asset_code,
				a.name AS invest_asset_name,
				a.name_common AS invest_asset_name_common,
				hr.employee_code AS requester,
				((((COALESCE(hr.title_th, ''::text) || ' '::text) || COALESCE(hr.first_name_th, ''::text)) || ' '::text) || COALESCE(hr.last_name_th, ''::text)) AS requester_name,
				sec.costcenter_code,
				sec.costcenter_name,
				sec.section_code,
				sec.section_name,
				sec.mission_code AS mission,
				sec.org_code,
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
				a.costcenter_id
			   FROM (((((((((res_invest_asset a
				 LEFT JOIN res_users u ON ((u.id = a.request_user_id)))
				 LEFT JOIN hr_employee h ON (((u.login)::text = (h.employee_code)::text)))
				 LEFT JOIN issi_hr_employee_view hr ON ((h.id = hr.id)))
				 LEFT JOIN etl_issi_m_section sec ON ((a.owner_section_id = sec.section_id)))
				 LEFT JOIN res_section ressec ON ((sec.section_id = ressec.id)))
				 LEFT JOIN res_program asecprg ON ((ressec.section_program_id = asecprg.id)))
				 LEFT JOIN account_fiscalyear fis ON ((a.fiscalyear_id = fis.id)))
				 LEFT JOIN res_program assetprg ON ((a.owner_program_id = assetprg.id)))
				 LEFT JOIN issi_m_program_view ownerprg ON ((a.owner_program_id = ownerprg.id))) 
		)
    """ % self._table)

class issi_m_personel_costcenter_view(models.Model):
    _name = 'issi.m.personel.costcenter.view'
    _auto = False
    _description = 'issi_m_personel_costcenter_view'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (  
			 SELECT s.id,
				s.code,
				COALESCE(irs.value, (s.name)::text) AS name,
				(s.name)::text AS name_en,
				o.id AS org_id,
				o.code AS org_code,
				COALESCE(iro.value, (o.name)::text) AS org_name,
				o.name AS org_name_en,
				COALESCE(iro_short.value, (o.name_short)::text) AS org_name_short,
				o.name_short AS org_name_short_en,
				sc.id AS sector_id,
				sc.code AS sector_code,
				COALESCE(irsc.value, (sc.name)::text) AS sector_name,
				COALESCE(irsc_short.value, (sc.name_short)::text) AS sector_name_short,
				(sc.name)::text AS sector_name_en,
				(sc.name_short)::text AS sector_name_short_en,
				sb.id AS subsector_id,
				sb.code AS subsector_code,
				COALESCE(irsb.value, (sb.name)::text) AS subsector_name,
				COALESCE(irsb_short.value, (sb.name_short)::text) AS subsector_name_short,
				(sb.name)::text AS subsector_name_en,
				(sb.name_short)::text AS subsector_name_short_en,
				d.id AS division_id,
				d.code AS division_code,
				COALESCE(ird.value, (d.name)::text) AS division_name,
				COALESCE(ird_short.value, (d.name_short)::text) AS division_name_short,
				(d.name)::text AS division_name_en,
				(d.name_short)::text AS division_name_short_en,
				c.id AS costcenter_id,
				c.code AS costcenter_code,
				COALESCE(irc.value, (c.name)::text) AS costcenter_name,
				COALESCE(irc_short.value, (c.name_short)::text) AS costcenter_name_short,
				(c.name)::text AS costcenter_name_en,
				(c.name_short)::text AS costcenter_name_short_en
			   FROM (((((((((((((((((res_personnel_costcenter s
				 LEFT JOIN res_org o ON ((s.org_id = o.id)))
				 LEFT JOIN res_sector sc ON ((s.sector_id = sc.id)))
				 LEFT JOIN res_subsector sb ON ((s.subsector_id = sb.id)))
				 LEFT JOIN res_division d ON ((s.division_id = d.id)))
				 LEFT JOIN res_costcenter c ON ((s.costcenter_id = c.id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.personnel.costcenter,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irs ON ((s.id = irs.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.org,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) iro ON ((s.org_id = iro.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) iro_short ON ((s.org_id = iro_short.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.costcenter,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irc ON ((s.costcenter_id = irc.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.costcenter,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irc_short ON ((s.costcenter_id = irc_short.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.sector,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsc ON ((s.sector_id = irsc.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.sector,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsc_short ON ((s.sector_id = irsc_short.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.subsector,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsb ON ((s.subsector_id = irsb.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.subsector,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) irsb_short ON ((s.subsector_id = irsb_short.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.division,name'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) ird ON ((s.division_id = ird.res_id)))
				 LEFT JOIN ( SELECT ir_translation.res_id,
						ir_translation.value
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.division,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) ird_short ON ((s.division_id = ird_short.res_id)))
				 LEFT JOIN res_mission miss ON ((miss.id = s.mission_id)))
			  ORDER BY s.code
		)
    """ % self._table)
	
class issi_m_source_budget_view(models.Model):
    _name = 'issi.m.source.budget.view'
    _auto = False
    _description = 'isis all master source of budget view'

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
