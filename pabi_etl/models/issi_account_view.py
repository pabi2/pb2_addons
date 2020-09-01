# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools

class issi_preprint_receipt(models.Model):
    _name = 'issi.preprint.receipt'
    _auto = False
    _description = u'รายงานใบเสร็จรับเงิน'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT rc.number_preprint AS preprint_number,
				rc.number AS doc_number,
				fy.name AS fiscal_year,
				p.name AS period,
				rc.date AS posting_pate,
				rc.date_document AS document_date,
				tx.code AS tax_branch,
				rc.narration AS information,
				cus.search_key AS partner_id,
				cus.display_name2 AS cus_name,
				rv.name AS document_origin,
				sys.name AS system_origin,
				inv.amount_untaxed AS amount,
				rc.tax_amount,
				emp.full_name_th AS validate_by,
				rc.state,
				''::text AS reverse_doc,
				inv.number AS invoice_number
			   FROM (((((((((((account_voucher rc
				 LEFT JOIN account_period p ON ((p.id = rc.period_id)))
				 LEFT JOIN account_fiscalyear fy ON ((fy.id = p.fiscalyear_id)))
				 LEFT JOIN account_voucher_line vl ON ((vl.voucher_id = rc.id)))
				 LEFT JOIN account_invoice inv ON ((inv.id = vl.invoice_id)))
				 LEFT JOIN res_taxbranch tx ON ((tx.id = inv.taxbranch_id)))
				 LEFT JOIN account_move am ON ((am.id = rc.move_id)))
				 LEFT JOIN res_partner cus ON ((cus.id = rc.partner_id)))
				 LEFT JOIN account_bank_receipt rv ON ((rv.id = rc.bank_receipt_id)))
				 LEFT JOIN interface_system sys ON ((sys.id = am.system_id)))
				 LEFT JOIN res_users usr ON ((usr.id = rc.validate_user_id)))
				 LEFT JOIN issi_hr_employee_view emp ON (((emp.employee_code)::text = (usr.login)::text)))
			  WHERE (((rc.type)::text = 'receipt'::text) AND ((rc.state)::text = ANY (ARRAY[('done'::character varying)::text, ('posted'::character varying)::text])))
			UNION ALL
			 SELECT ia.preprint_number,
				am.name AS doc_number,
				fy.name AS fiscal_year,
				p.name AS period,
				am.date AS posting_pate,
				am.date_document AS document_date,
				tx.code AS tax_branch,
				am.narration AS information,
				cus.search_key AS partner_id,
				cus.display_name2 AS cus_name,
				am.ref AS document_origin,
				sys.name AS system_origin,
				aml.debit AS amount,
				aml.tax_amount,
				emp.full_name_th AS validate_by,
				ia.state,
				''::text AS reverse_doc,
				''::text AS invoice_number
			   FROM ((((((((((account_move am
				 LEFT JOIN interface_account_entry ia ON ((ia.move_id = am.id)))
				 LEFT JOIN account_period p ON ((p.id = am.period_id)))
				 LEFT JOIN account_fiscalyear fy ON ((fy.id = p.fiscalyear_id)))
				 LEFT JOIN account_move_line aml ON ((aml.move_id = am.id)))
				 LEFT JOIN res_taxbranch tx ON ((tx.id = aml.taxbranch_id)))
				 LEFT JOIN res_partner cus ON ((cus.id = am.partner_id)))
				 LEFT JOIN interface_system sys ON ((sys.id = am.system_id)))
				 LEFT JOIN interface_account_entry ia2 ON (((ia2.number)::text = (am.name)::text)))
				 LEFT JOIN res_users usr ON ((usr.id = ia2.validate_user_id)))
				 LEFT JOIN issi_hr_employee_view emp ON (((emp.employee_code)::text = (usr.login)::text)))
			  WHERE (((aml.doctype)::text = 'interface_account'::text) AND (aml.bank_receipt_id IS NOT NULL) AND ((ia.state)::text = ANY (ARRAY[('done'::character varying)::text, ('posted'::character varying)::text])))
			UNION ALL
			 SELECT rc.number_preprint AS preprint_number,
				rc.number AS doc_number,
				fy.name AS fiscal_year,
				p.name AS period,
				rc.date AS posting_pate,
				rc.date_document AS document_date,
				tx.code AS tax_branch,
				rc.narration AS information,
				cus.search_key AS partner_id,
				cus.display_name2 AS cus_name,
				rv.name AS document_origin,
				sys.name AS system_origin,
				inv.amount_untaxed AS amount,
				rc.tax_amount,
				emp.full_name_th AS validate_by,
				rc.state,
				cv.name AS reverse_doc,
				inv.number AS invoice_number
			   FROM ((((((((((((account_voucher rc
				 LEFT JOIN account_period p ON ((p.id = rc.period_id)))
				 LEFT JOIN account_fiscalyear fy ON ((fy.id = p.fiscalyear_id)))
				 LEFT JOIN account_voucher_line vl ON ((vl.voucher_id = rc.id)))
				 LEFT JOIN account_invoice inv ON ((inv.id = vl.invoice_id)))
				 LEFT JOIN res_taxbranch tx ON ((tx.id = inv.taxbranch_id)))
				 LEFT JOIN account_move am ON ((am.id = rc.move_id)))
				 LEFT JOIN res_partner cus ON ((cus.id = rc.partner_id)))
				 LEFT JOIN account_bank_receipt rv ON ((rv.id = rc.bank_receipt_id)))
				 LEFT JOIN interface_system sys ON ((sys.id = am.system_id)))
				 LEFT JOIN res_users usr ON ((usr.id = rc.validate_user_id)))
				 LEFT JOIN issi_hr_employee_view emp ON (((emp.employee_code)::text = (usr.login)::text)))
				 LEFT JOIN account_move cv ON ((cv.id = rc.cancel_move_id)))
			  WHERE (((rc.type)::text = 'receipt'::text) AND (rc.number IS NOT NULL) AND ((rc.state)::text = 'cancel'::text) AND (rc.number_preprint IS NOT NULL))		
        )
        """ % self._table)			

class issi_account_av_balance(models.Model):
    _name = 'issi.account.av.balance'
    _auto = False
    _description = u'PB2-RT008 รายงานเงินยืมคงค้าง'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT av.id AS av_id,
				av.number AS av_number,
				av.name AS description,
				hr.employee_code,
				hr.display_name_th AS name_th,
				av.date AS approve_date,
				av.date_due AS due_date,
				(date(now()) - av.date_due) AS balance_day,
				av.amount_advanced AS advanced_amount,
				av.amount_to_clearing AS advance_balance,
				avline.chart_view,
					CASE avline.chart_view
						WHEN 'unit_base'::text THEN cctr.costcenter_code
						WHEN 'project_base'::text THEN prj.section_code
						WHEN 'invest_asset'::text THEN invass.section_code
						WHEN 'invest_construction'::text THEN cons.section_code
						WHEN 'personnel'::text THEN pers.section_code
						ELSE ''::character varying
					END AS section_code,
				avline.costcenter_id AS cctr_id,
				cctr.costcenter_code AS cctr_code,
				avline.project_id,
				avline.invest_asset_id,
				avline.invest_construction_id,
				avline.personnel_costcenter_id,
					CASE avline.chart_view
						WHEN 'unit_base'::text THEN cctr.costcenter_code
						WHEN 'project_base'::text THEN prj.source_budget
						WHEN 'invest_asset'::text THEN invass.source_budget
						WHEN 'invest_construction'::text THEN cons.source_budget
						WHEN 'personnel'::text THEN pers.source_budget
						ELSE ''::character varying
					END AS source_budget,
					CASE avline.chart_view
						WHEN 'unit_base'::text THEN cctr.costcenter_name
						WHEN 'project_base'::text THEN prj.source_budget_name
						WHEN 'invest_asset'::text THEN invass.source_budget_name
						WHEN 'invest_construction'::text THEN cons.source_budget_name
						WHEN 'personnel'::text THEN pers.source_budget_name
						ELSE ''::text
					END AS source_budget_name
			   FROM ((((((((hr_expense_expense av
				 LEFT JOIN hr_expense_line avline ON ((avline.expense_id = av.id)))
				 LEFT JOIN issi_hr_employee_view hr ON ((hr.id = av.employee_id)))
				 LEFT JOIN issi_m_source_budget_view sec ON ((avline.section_id = sec.section_id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((avline.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN issi_m_source_budget_view prj ON ((avline.project_id = prj.project_id)))
				 LEFT JOIN issi_m_source_budget_view invass ON ((avline.invest_asset_id = invass.invest_asset_id)))
				 LEFT JOIN issi_m_source_budget_view cons ON ((avline.invest_construction_id = cons.invest_construction_phase_id)))
				 LEFT JOIN issi_m_source_budget_view pers ON ((avline.personnel_costcenter_id = pers.personnel_costcenter_id)))
			  WHERE ((av.is_employee_advance = true) AND ((av.state)::text = 'paid'::text) AND (av.amount_to_clearing > (1)::double precision))
        )
        """ % self._table)

class report_internal_charge_expense(models.Model):
    _name = 'report.internal.charge.expense'
    _auto = False
    _description = 'Internal Charge Expense Report'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT fiscal.name AS fiscal_year,
				"left"((period.name)::text, 2) AS period,
				hr.number AS web_doc,
				hrl.name AS line_item_text,
				mov_rev.name AS doc_no_rev,
				mov_rev.doctype AS doc_type_rev,
				mov_rev.date_document AS doc_date_rev,
				mov_rev.date AS post_date_rev,
				org_th_rev.name_short_th AS org_rev,
				ag_rev.code AS ag_code_rev,
				ag_rev.name AS ag_name_rev,
				a_rev.code AS a_code_rev,
				a_rev.name AS a_name_rev,
				acct_rev.code AS account_code_rev,
				acct_rev.name AS account_name_rev,
					CASE
						WHEN (prj_rev.code IS NOT NULL) THEN 'project'::text
						ELSE 'section'::text
					END AS type_rev,
				sec_rev.code AS profit_code_rev,
				sec_rev2.section_name AS profit_name_rev,
				prj_rev.code AS project_code_rev,
				prj_rev.name AS project_name_rev,
				cct_rev.code AS cctr_code_rev,
				sec_rev2.costcenter_name AS cctr_name_rev,
				mis_rev.name AS mission_name_rev,
				mov_exp.name AS doc_no_exp,
				mov_exp.doctype AS doc_type_exp,
				mov_exp.date_document AS doc_date_exp,
				mov_exp.date AS post_date_exp,
				org_th_exp.name_short_th AS org_exp,
				ag_exp.code AS ag_code_exp,
				ag_exp.name AS ag_name_exp,
				a_exp.code AS a_code_exp,
				a_exp.name AS a_name_exp,
				acct_exp.code AS account_code_exp,
				acct_exp.name AS account_name_exp,
					CASE
						WHEN (prj_exp.code IS NOT NULL) THEN 'project'::text
						ELSE 'section'::text
					END AS type_exp,
				sec_exp.code AS profit_code_exp,
				sec_exp2.section_name AS profit_name_exp,
				prj_exp.code AS project_code_exp,
				prj_exp.name AS project_name_exp,
				cct_exp2.code AS cctr_code_exp,
				sec_exp2.costcenter_name AS cctr_name_exp,
				mis_exp.name AS mission_name_exp,
				hrl.total_amount,
				mov_rev.create_date AS posting_date
			   FROM ((((((((((((((((((((((((((hr_expense_expense hr
				 JOIN hr_expense_line hrl ON ((hrl.expense_id = hr.id)))
				 JOIN account_period period ON (((period.date_start <= hr.date) AND (period.date_stop >= hr.date) AND ("left"((period.code)::text, 2) <> '00'::text))))
				 JOIN account_fiscalyear fiscal ON ((fiscal.id = period.fiscalyear_id)))
				 JOIN account_move mov_rev ON ((mov_rev.id = hr.rev_ic_move_id)))
				 LEFT JOIN account_activity_group ag_rev ON ((ag_rev.id = hrl.inrev_activity_group_id)))
				 LEFT JOIN account_activity a_rev ON ((a_rev.id = hrl.inrev_activity_id)))
				 JOIN account_account acct_rev ON ((acct_rev.id = a_rev.account_id)))
				 JOIN res_section sec_rev ON ((sec_rev.id = hr.internal_section_id)))
				 JOIN etl_issi_m_section sec_rev2 ON (((sec_rev2.section_code)::text = (sec_rev.code)::text)))
				 JOIN res_org org_rev ON ((org_rev.id = sec_rev.org_id)))
				 JOIN ( SELECT ir_translation.res_id AS org_id,
						ir_translation.value AS name_short_th
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) org_th_rev ON ((org_th_rev.org_id = org_rev.id)))
				 LEFT JOIN res_project prj_rev ON ((prj_rev.id = hr.internal_project_id)))
				 JOIN res_costcenter cct_rev ON ((cct_rev.id = sec_rev.costcenter_id)))
				 JOIN res_mission mis_rev ON ((mis_rev.id = sec_rev.mission_id)))
				 JOIN account_move mov_exp ON ((mov_exp.id = hr.exp_ic_move_id)))
				 LEFT JOIN account_activity_group ag_exp ON ((ag_exp.id = hrl.activity_group_id)))
				 LEFT JOIN account_activity a_exp ON ((a_exp.id = hrl.activity_id)))
				 JOIN account_account acct_exp ON ((acct_exp.id = a_exp.account_id)))
				 JOIN res_costcenter cct_exp ON ((cct_exp.id = hrl.costcenter_id)))
				 JOIN res_section sec_exp ON (((sec_exp.code)::text = (cct_exp.code)::text)))
				 JOIN etl_issi_m_section sec_exp2 ON (((sec_exp2.section_code)::text = (sec_exp.code)::text)))
				 JOIN res_org org_exp ON ((org_exp.id = sec_exp.org_id)))
				 JOIN ( SELECT ir_translation.res_id AS org_id,
						ir_translation.value AS name_short_th
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) org_th_exp ON ((org_th_exp.org_id = org_rev.id)))
				 LEFT JOIN res_project prj_exp ON ((prj_exp.id = hrl.project_id)))
				 JOIN res_costcenter cct_exp2 ON ((cct_exp2.id = sec_exp.costcenter_id)))
				 JOIN res_mission mis_exp ON ((mis_exp.id = sec_exp.mission_id)))
			  WHERE ((hr.state)::text = 'paid'::text)
			UNION ALL
			 SELECT fiscal.name AS fiscal_year,
				"left"((period.name)::text, 2) AS period,
				hr.number AS web_doc,
				hrl.name AS line_item_text,
				mov_rev.name AS doc_no_rev,
				mov_rev.doctype AS doc_type_rev,
				mov_rev.date_document AS doc_date_rev,
				mov_rev.date AS post_date_rev,
				org_th_rev.name_short_th AS org_rev,
				ag_rev.code AS ag_code_rev,
				ag_rev.name AS ag_name_rev,
				a_rev.code AS a_code_rev,
				a_rev.name AS a_name_rev,
				acct_rev.code AS account_code_rev,
				acct_rev.name AS account_name_rev,
					CASE
						WHEN (prj_rev.code IS NOT NULL) THEN 'project'::text
						ELSE 'section'::text
					END AS type_rev,
				sec_rev.code AS profit_code_rev,
				sec_rev2.section_name AS profit_name_rev,
				prj_rev.code AS project_code_rev,
				prj_rev.name AS project_name_rev,
				cct_rev.code AS cctr_code_rev,
				sec_rev2.costcenter_name AS cctr_name_rev,
				mis_rev.name AS mission_name_rev,
				mov_exp.name AS doc_no_exp,
				mov_exp.doctype AS doc_type_exp,
				mov_exp.date_document AS doc_date_exp,
				mov_exp.date AS post_date_exp,
				org_th_exp.name_short_th AS org_exp,
				ag_exp.code AS ag_code_exp,
				ag_exp.name AS ag_name_exp,
				a_exp.code AS a_code_exp,
				a_exp.name AS a_name_exp,
				acct_exp.code AS account_code_exp,
				acct_exp.name AS account_name_exp,
					CASE
						WHEN (prj_exp.code IS NOT NULL) THEN 'project'::text
						ELSE 'section'::text
					END AS type_exp,
				sec_exp.code AS profit_code_exp,
				sec_exp2.section_name AS profit_name_exp,
				prj_exp.code AS project_code_exp,
				prj_exp.name AS project_name_exp,
				cct_exp2.code AS cctr_code_exp,
				sec_exp2.costcenter_name AS cctr_name_exp,
				mis_exp.name AS mission_name_exp,
				hrl.total_amount,
				mov_rev.create_date AS posting_date
			   FROM (((((((((((((((((((((((((((hr_expense_expense hr
				 JOIN hr_expense_line hrl ON ((hrl.expense_id = hr.id)))
				 JOIN account_period period ON (((period.date_start <= hr.date) AND (period.date_stop >= hr.date) AND ("left"((period.code)::text, 2) <> '00'::text))))
				 JOIN account_fiscalyear fiscal ON ((fiscal.id = period.fiscalyear_id)))
				 JOIN account_move mov_rev ON ((mov_rev.id = hr.rev_ic_move_id)))
				 LEFT JOIN account_activity_group ag_rev ON ((ag_rev.id = hrl.inrev_activity_group_id)))
				 LEFT JOIN account_activity a_rev ON ((a_rev.id = hrl.inrev_activity_id)))
				 JOIN account_account acct_rev ON ((acct_rev.id = a_rev.account_id)))
				 JOIN res_project prj_rev ON ((prj_rev.id = hr.internal_project_id)))
				 JOIN hr_employee emp_rev ON ((emp_rev.id = prj_rev.pm_employee_id)))
				 JOIN res_section sec_rev ON ((sec_rev.id = emp_rev.section_id)))
				 JOIN etl_issi_m_section sec_rev2 ON (((sec_rev2.section_code)::text = (sec_rev.code)::text)))
				 JOIN res_org org_rev ON ((org_rev.id = sec_rev.org_id)))
				 JOIN ( SELECT ir_translation.res_id AS org_id,
						ir_translation.value AS name_short_th
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) org_th_rev ON ((org_th_rev.org_id = org_rev.id)))
				 JOIN res_costcenter cct_rev ON ((cct_rev.id = sec_rev.costcenter_id)))
				 JOIN res_mission mis_rev ON ((mis_rev.id = sec_rev.mission_id)))
				 JOIN account_move mov_exp ON ((mov_exp.id = hr.exp_ic_move_id)))
				 LEFT JOIN account_activity_group ag_exp ON ((ag_exp.id = hrl.activity_group_id)))
				 LEFT JOIN account_activity a_exp ON ((a_exp.id = hrl.activity_id)))
				 JOIN account_account acct_exp ON ((acct_exp.id = a_exp.account_id)))
				 JOIN res_costcenter cct_exp ON ((cct_exp.id = hrl.costcenter_id)))
				 JOIN res_section sec_exp ON (((sec_exp.code)::text = (cct_exp.code)::text)))
				 JOIN etl_issi_m_section sec_exp2 ON (((sec_exp2.section_code)::text = (sec_exp.code)::text)))
				 JOIN res_org org_exp ON ((org_exp.id = sec_exp.org_id)))
				 JOIN ( SELECT ir_translation.res_id AS org_id,
						ir_translation.value AS name_short_th
					   FROM ir_translation
					  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) org_th_exp ON ((org_th_exp.org_id = org_rev.id)))
				 LEFT JOIN res_project prj_exp ON ((prj_exp.id = hrl.project_id)))
				 JOIN res_costcenter cct_exp2 ON ((cct_exp2.id = sec_exp.costcenter_id)))
				 JOIN res_mission mis_exp ON ((mis_exp.id = sec_exp.mission_id)))
			  WHERE ((hr.state)::text = 'paid'::text)
		)
    """ % self._table)

class report_internal_charge_interface(models.Model):
    _name = 'report.internal.charge.interface'
    _auto = False
    _description = 'Internal Charge Interface Report'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT rev.fiscal_year,
				rev.period,
				rev.web_doc,
				rev.item_text_rev,
				rev.doc_no_rev,
				rev.doc_type_rev,
				rev.doc_date_rev,
				rev.post_date_rev,
				rev.org_rev,
				rev.ag_code_rev,
				rev.ag_name_rev,
				rev.a_code_rev,
				rev.a_name_rev,
				rev.account_code_rev,
				rev.account_name_rev,
					CASE
						WHEN (rev.project_code_rev IS NOT NULL) THEN 'project'::text
						ELSE 'section'::text
					END AS type_rev,
				rev.profit_code_rev,
				rev.profit_name_rev,
				rev.project_code_rev,
				rev.project_name_rev,
				rev.cctr_code_rev,
				rev.cctr_name_rev,
				rev.mission_name_rev,
				exp.doc_no_exp,
				exp.doc_type_exp,
				exp.doc_date_exp,
				exp.post_date_exp,
				exp.org_exp,
				exp.ag_code_exp,
				exp.ag_name_exp,
				exp.a_code_exp,
				exp.a_name_exp,
				exp.account_code_exp,
				exp.account_name_exp,
					CASE
						WHEN (exp.project_code_exp IS NOT NULL) THEN 'project'::text
						ELSE 'section'::text
					END AS type_exp,
				exp.profit_code_exp,
				exp.profit_name_exp,
				exp.project_code_exp,
				exp.project_name_exp,
				exp.cctr_code_exp,
				exp.cctr_name_exp,
				exp.mission_name_exp,
				exp.total_amount_exp AS total_amount,
				exp.posting_date
			   FROM ((( SELECT fiscal.name AS fiscal_year,
						"left"((period.name)::text, 2) AS period,
						ia_rev.name AS web_doc,
						movl_rev.name AS item_text_rev,
						ia_rev.number AS doc_no_rev,
						mov_rev.doctype AS doc_type_rev,
						mov_rev.date_document AS doc_date_rev,
						mov_rev.date AS post_date_rev,
						org_th_rev.name_short_th AS org_rev,
						ag_rev.code AS ag_code_rev,
						ag_rev.name AS ag_name_rev,
						a_rev.code AS a_code_rev,
						a_rev.name AS a_name_rev,
						acct_rev.code AS account_code_rev,
						acct_rev.name AS account_name_rev,
						cct_rev.code AS cctr_code_rev,
						sec_rev2.costcenter_name AS cctr_name_rev,
						prj_rev.code AS project_code_rev,
						prj_rev.name AS project_name_rev,
						sec_rev.code AS profit_code_rev,
						sec_rev2.section_name AS profit_name_rev,
						mis_rev.name AS mission_name_rev,
							CASE
								WHEN ((ia_rev.type)::text = 'reverse'::text) THEN (abs((movl_rev.credit - movl_rev.debit)) * ('-1'::integer)::numeric)
								WHEN ((ia_rev.type)::text = 'invoice'::text) THEN abs((movl_rev.credit - movl_rev.debit))
								ELSE NULL::numeric
							END AS total_amount_rev,
						a_rev.id AS a_id_rev
					   FROM ((((((((((((((interface_account_entry ia_rev
						 JOIN account_move mov_rev ON ((mov_rev.id = ia_rev.move_id)))
						 JOIN account_move_line movl_rev ON ((movl_rev.move_id = mov_rev.id)))
						 JOIN account_account acct_rev ON ((acct_rev.id = movl_rev.account_id)))
						 JOIN account_account_type acctype_rev ON (((acctype_rev.id = acct_rev.user_type) AND ((acctype_rev.code)::text = 'Revenue'::text))))
						 LEFT JOIN account_activity_group ag_rev ON ((ag_rev.id = movl_rev.activity_group_id)))
						 LEFT JOIN account_activity a_rev ON ((a_rev.id = movl_rev.activity_id)))
						 JOIN account_period period ON ((period.id = movl_rev.period_id)))
						 JOIN account_fiscalyear fiscal ON ((fiscal.id = period.fiscalyear_id)))
						 JOIN res_costcenter cct_rev ON ((cct_rev.id = movl_rev.costcenter_id)))
						 LEFT JOIN res_project prj_rev ON ((prj_rev.id = movl_rev.project_id)))
						 JOIN ( SELECT ir_translation.res_id AS org_id,
								ir_translation.value AS name_short_th
							   FROM ir_translation
							  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) org_th_rev ON ((org_th_rev.org_id = movl_rev.org_id)))
						 LEFT JOIN res_section sec_rev ON ((sec_rev.id = movl_rev.section_id)))
						 JOIN etl_issi_m_section sec_rev2 ON (((sec_rev2.section_code)::text = (sec_rev.code)::text)))
						 JOIN res_mission mis_rev ON ((mis_rev.id = movl_rev.mission_id)))
					  WHERE ((ia_rev.charge_type)::text = 'internal'::text)) rev
				 JOIN activity_inrev_activity_rel rel ON ((rev.a_id_rev = rel.inrev_activity_id)))
				 JOIN ( SELECT ia_exp.number AS doc_no_exp,
						mov_exp.doctype AS doc_type_exp,
						mov_exp.date_document AS doc_date_exp,
						mov_exp.date AS post_date_exp,
						org_th_exp.name_short_th AS org_exp,
						ag_exp.code AS ag_code_exp,
						ag_exp.name AS ag_name_exp,
						a_exp.code AS a_code_exp,
						a_exp.name AS a_name_exp,
						acct_exp.code AS account_code_exp,
						acct_exp.name AS account_name_exp,
						cct_exp.code AS cctr_code_exp,
						sec_exp2.costcenter_name AS cctr_name_exp,
						prj_exp.code AS project_code_exp,
						prj_exp.name AS project_name_exp,
						sec_exp.code AS profit_code_exp,
						sec_exp2.section_name AS profit_name_exp,
						mis_exp.name AS mission_name_exp,
							CASE
								WHEN ((ia_exp.type)::text = 'reverse'::text) THEN (abs((movl_exp.credit - movl_exp.debit)) * ('-1'::integer)::numeric)
								WHEN ((ia_exp.type)::text = 'invoice'::text) THEN abs((movl_exp.credit - movl_exp.debit))
								ELSE NULL::numeric
							END AS total_amount_exp,
						movl_exp.name AS item_text_exp,
						a_exp.id AS a_id_exp,
						ia_exp.create_date AS posting_date
					   FROM ((((((((((((interface_account_entry ia_exp
						 JOIN account_move mov_exp ON ((mov_exp.id = ia_exp.move_id)))
						 JOIN account_move_line movl_exp ON ((movl_exp.move_id = mov_exp.id)))
						 JOIN account_account acct_exp ON ((acct_exp.id = movl_exp.account_id)))
						 JOIN account_account_type acctype_exp ON (((acctype_exp.id = acct_exp.user_type) AND ((acctype_exp.code)::text = 'Expense'::text))))
						 LEFT JOIN account_activity_group ag_exp ON ((ag_exp.id = movl_exp.activity_group_id)))
						 LEFT JOIN account_activity a_exp ON ((a_exp.id = movl_exp.activity_id)))
						 JOIN res_costcenter cct_exp ON ((cct_exp.id = movl_exp.costcenter_id)))
						 LEFT JOIN res_project prj_exp ON ((prj_exp.id = movl_exp.project_id)))
						 JOIN ( SELECT ir_translation.res_id AS org_id,
								ir_translation.value AS name_short_th
							   FROM ir_translation
							  WHERE (((ir_translation.name)::text = 'res.org,name_short'::text) AND ((ir_translation.type)::text = 'model'::text) AND ((ir_translation.lang)::text = 'th_TH'::text))) org_th_exp ON ((org_th_exp.org_id = movl_exp.org_id)))
						 LEFT JOIN res_section sec_exp ON ((sec_exp.id = movl_exp.section_id)))
						 JOIN etl_issi_m_section sec_exp2 ON (((sec_exp2.section_code)::text = (sec_exp.code)::text)))
						 JOIN res_mission mis_exp ON ((mis_exp.id = movl_exp.mission_id)))
					  WHERE ((ia_exp.charge_type)::text = 'internal'::text)) exp ON ((rel.inexp_activity_id = exp.a_id_exp)))
			  WHERE (((exp.item_text_exp)::text = (rev.item_text_rev)::text) AND (rev.total_amount_rev = exp.total_amount_exp))
		)
    """ % self._table)

class etl_issi_account_query(models.Model):
    _name = 'etl.issi.account.query'
    _auto = False
    _description = 'etl_issi_account_query'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE VIEW %s as (
			 SELECT "right"((perd.code)::text, 4) AS fiscal_year,
				"left"((perd.code)::text, 2) AS period,
				bb.charge_type,
				act.code AS account_code,
				act.name AS account_name,
				job.public AS nstda_wide,
				jobtype.code AS job_order_type,
				jobtype.name AS job_order_type_name,
				job.code AS job_order,
				job.name AS job_order_name,
				ag.code AS activity_group,
				ag.name AS activity_group_name,
				av.code AS activity,
				av.name AS activity_name,
				arpt.code AS activity_rpt,
				arpt.name AS activity_rpt_name,
					CASE
						WHEN (bb.check_chart_view = 'invest_construction'::text) THEN bgcon.org_code
						WHEN (bb.check_chart_view = 'invest_asset'::text) THEN invasset_sec.org_code
						WHEN (bb.check_chart_view = 'project_base'::text) THEN prjsec.org_code
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN sec2.org_code
						WHEN (bb.check_chart_view = 'personnel'::text) THEN budper.org_code
						ELSE org.code
					END AS org_code,
					CASE
						WHEN (bb.check_chart_view = 'invest_construction'::text) THEN bgcon.org_name_short
						WHEN (bb.check_chart_view = 'invest_asset'::text) THEN invasset_sec.org_name_short_en
						WHEN (bb.check_chart_view = 'project_base'::text) THEN prjsec.org_name_short_en
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN sec2.org_name_short_en
						WHEN (bb.check_chart_view = 'personnel'::text) THEN budper.org_name_short_en
						ELSE org.name_short
					END AS org_name,
					CASE
						WHEN (bb.check_chart_view = 'invest_construction'::text) THEN bgcon.code
						WHEN (bb.check_chart_view = 'invest_asset'::text) THEN bgasset.code
						WHEN (bb.check_chart_view = 'project_base'::text) THEN prj.project_code
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN sec2.section_code
						WHEN (bb.check_chart_view = 'personnel'::text) THEN budper.code
						ELSE ''::character varying
					END AS source_budget_code,
					CASE
						WHEN (bb.check_chart_view = 'invest_construction'::text) THEN bgcon.phase_name
						WHEN (bb.check_chart_view = 'invest_asset'::text) THEN bgasset.name
						WHEN (bb.check_chart_view = 'project_base'::text) THEN (prj.project_name)::character varying
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN (replace(sec2.section_name, '[ไม่ใช้งาน] '::text, ''::text))::character varying
						WHEN (bb.check_chart_view = 'personnel'::text) THEN (budper.name)::character varying
						ELSE ''::character varying
					END AS source_budget_name,
				aal.chart_view AS source_budget,
				cctr.costcenter_code AS costcenter,
				replace(cctr.costcenter_name, '[ไม่ใช้งาน] '::text, ''::text) AS costcenter_name,
				bgcon.construction_code AS project_c_code,
				bgcon.construction_name AS project_c_name,
					CASE
						WHEN (bb.check_chart_view = 'invest_construction'::text) THEN bgcon.mission
						WHEN (bb.check_chart_view = 'invest_asset'::text) THEN bgcon.mission
						WHEN (bb.check_chart_view = 'project_base'::text) THEN prj.mission
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN (sec2.mission_code)::character varying
						WHEN (bb.check_chart_view = 'personnel'::text) THEN 'IM'::character varying
						ELSE miss.name
					END AS mission,
					CASE
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN ressecpg.code
						WHEN (bb.check_chart_view = 'project_base'::text) THEN prjsecpg.code
						ELSE secpg.code
					END AS section_program,
					CASE
						WHEN (bb.check_chart_view = 'unit_base'::text) THEN ressecpg.name
						WHEN (bb.check_chart_view = 'project_base'::text) THEN prjsecpg.name
						ELSE secpg.name
					END AS section_program_name,
				bb.amount,
				bb.check_chart_view,
				bb.move_line_id,
				bb.document,
				bb.docline_seq,
				bb.detail,
				bb.doc_date,
				bb.create_date,
				partner.search_key AS partner_code,
				partner.display_name2 AS partner_name,
				cat.name AS partner_category,
				bb.move_write_date,
				bb.move_state,
				bb.move_line_state,
				bb.document_ref_id,
				bb.document_ref AS model_ref,
					CASE
						WHEN (bb.document_ref = 'interface_account_entry'::text) THEN ref_interface.name
						WHEN (bb.document_ref = 'hr_expense_expense'::text) THEN ref_hrexp.number
						WHEN (bb.document_ref = 'stock_picking'::text) THEN ref_stock.stock_picking_origin
						WHEN (bb.document_ref = 'account_invoice'::text) THEN ref_invoice.source_document
						WHEN (bb.document_ref = 'hr_salary_expense'::text) THEN ref_salary.number
						ELSE ''::character varying
					END AS document_ref,
					CASE
						WHEN (bb.document_ref = 'hr_expense_expense'::text) THEN exp_hrreq.employee_code
						WHEN (bb.document_ref = 'stock_picking'::text) THEN ref_stock.requested_by
						WHEN (bb.document_ref = 'account_invoice'::text) THEN ref_invoice.requested_by
						WHEN (bb.document_ref = 'hr_salary_expense'::text) THEN sal_hrreq.employee_code
						ELSE ''::character varying
					END AS requester,
					CASE
						WHEN (bb.document_ref = 'hr_expense_expense'::text) THEN exp_hrreq.full_name_th
						WHEN (bb.document_ref = 'stock_picking'::text) THEN ref_stock.requested_by_name
						WHEN (bb.document_ref = 'account_invoice'::text) THEN ref_invoice.requested_by_name
						WHEN (bb.document_ref = 'hr_salary_expense'::text) THEN sal_hrreq.full_name_th
						ELSE ''::text
					END AS requester_name,
					CASE
						WHEN (bb.document_ref = 'interface_account_entry'::text) THEN interface_hrapp.employee_code
						WHEN (bb.document_ref = 'hr_expense_expense'::text) THEN exp_hrapp.employee_code
						WHEN (bb.document_ref = 'stock_picking'::text) THEN ref_stock.approver
						WHEN (bb.document_ref = 'account_invoice'::text) THEN ref_invoice.approver
						WHEN (bb.document_ref = 'hr_salary_expense'::text) THEN sal_hrapp.employee_code
						ELSE ''::character varying
					END AS approver,
					CASE
						WHEN (bb.document_ref = 'interface_account_entry'::text) THEN interface_hrapp.full_name_th
						WHEN (bb.document_ref = 'hr_expense_expense'::text) THEN exp_hrapp.full_name_th
						WHEN (bb.document_ref = 'stock_picking'::text) THEN ref_stock.approver_name
						WHEN (bb.document_ref = 'account_invoice'::text) THEN ref_invoice.approver_name
						WHEN (bb.document_ref = 'hr_salary_expense'::text) THEN sal_hrapp.full_name_th
						ELSE ''::text
					END AS approver_name,
				bb.posting_date,
				ref_system.name AS system_ref
			   FROM ((((((((((((((((((((((((((((((((((((((((((( SELECT aa.charge_type,
						aa.chart_view,
						aa.period_id,
						aa.activity_group_id,
						aa.activity_id,
						aa.activity_rpt_id,
						aa.account_id,
						aa.org_id,
						aa.costcenter_id,
						aa.section_id,
						aa.section_program_id,
						aa.project_id,
						aa.mission_id,
						aa.doctype,
						aa.cost_control_type_id,
						aa.cost_control_id,
						aa.analytic_account_id,
						aa.invest_construction_phase_id,
						aa.invest_asset_id,
						aa.personnel_costcenter_id,
						sum((aa.debit - aa.credit)) AS amount,
						aa.state,
							CASE
								WHEN (aa.invest_construction_phase_id IS NOT NULL) THEN 'invest_construction'::text
								WHEN (aa.invest_asset_id IS NOT NULL) THEN 'invest_asset'::text
								WHEN (aa.project_id IS NOT NULL) THEN 'project_base'::text
								WHEN (aa.section_id IS NOT NULL) THEN 'unit_base'::text
								WHEN (aa.personnel_costcenter_id IS NOT NULL) THEN 'personnel'::text
								ELSE ''::text
							END AS check_chart_view,
						aa.id AS move_line_id,
						acctmoved.name AS document,
						aa.docline_seq,
						aa.name AS detail,
						acctmoved.date_document AS doc_date,
						date(aa.create_date) AS create_date,
						date(acctmoved.write_date) AS move_write_date,
						aa.partner_id,
						acctmoved.state AS move_state,
						aa.state AS move_line_state,
						replace("substring"((aa.document_id)::text, 0, "position"((aa.document_id)::text, ','::text)), '.'::text, '_'::text) AS document_ref,
						to_number("substring"((aa.document_id)::text, ("position"((aa.document_id)::text, ','::text) + 1)), '999999999'::text) AS document_ref_id,
						acctmoved.date AS posting_date
					   FROM (account_move_line aa
						 LEFT JOIN account_move acctmoved ON ((aa.move_id = acctmoved.id)))
					  GROUP BY aa.charge_type, aa.chart_view, aa.period_id, aa.activity_group_id, aa.activity_id, aa.activity_rpt_id, aa.account_id, aa.org_id, aa.costcenter_id, aa.section_id, aa.section_program_id, aa.project_id, aa.mission_id, aa.doctype, aa.cost_control_type_id, aa.cost_control_id, aa.analytic_account_id, aa.state, aa.invest_construction_phase_id, aa.invest_asset_id, aa.personnel_costcenter_id, aa.id, acctmoved.name, aa.docline_seq, aa.name, aa.create_date, acctmoved.date_document, aa.partner_id, (date(acctmoved.write_date)), acctmoved.state, aa.document_id, acctmoved.date) bb
				 LEFT JOIN account_period perd ON ((bb.period_id = perd.id)))
				 LEFT JOIN account_account act ON ((bb.account_id = act.id)))
				 LEFT JOIN account_activity_group ag ON ((bb.activity_group_id = ag.id)))
				 LEFT JOIN account_activity av ON ((bb.activity_id = av.id)))
				 LEFT JOIN res_org org ON ((bb.org_id = org.id)))
				 LEFT JOIN account_activity arpt ON ((bb.activity_rpt_id = arpt.id)))
				 LEFT JOIN account_analytic_account aal ON ((bb.analytic_account_id = aal.id)))
				 LEFT JOIN res_mission miss ON ((bb.mission_id = miss.id)))
				 LEFT JOIN etl_issi_m_section sec2 ON ((bb.section_id = sec2.section_id)))
				 LEFT JOIN res_section res_sec ON ((bb.section_id = res_sec.id)))
				 LEFT JOIN res_section_program ressecpg ON ((res_sec.section_program_id = ressecpg.id)))
				 LEFT JOIN res_section_program secpg ON ((bb.section_program_id = secpg.id)))
				 LEFT JOIN etl_issi_m_costcenter cctr ON ((bb.costcenter_id = cctr.costcenter_id)))
				 LEFT JOIN etl_issi_m_project prj ON ((bb.project_id = prj.pb2_project_id)))
				 LEFT JOIN etl_issi_m_section prjsec ON ((prj.pm_section_id = prjsec.section_id)))
				 LEFT JOIN res_project res_prj ON ((bb.project_id = res_prj.id)))
				 LEFT JOIN res_section_program prjsecpg ON ((res_prj.program_id = prjsecpg.id)))
				 LEFT JOIN issi_m_investment_construction_phase_view bgcon ON ((bb.invest_construction_phase_id = bgcon.invest_construction_phase_id)))
				 LEFT JOIN etl_issi_m_section bgconsec ON ((bgcon.pm_section_id = bgconsec.section_id)))
				 LEFT JOIN res_invest_asset bgasset ON ((bb.invest_asset_id = bgasset.id)))
				 LEFT JOIN etl_issi_m_section invasset_sec ON ((bgasset.owner_section_id = invasset_sec.section_id)))
				 LEFT JOIN issi_m_personel_costcenter_view budper ON ((bb.personnel_costcenter_id = budper.id)))
				 LEFT JOIN etl_issi_m_section persec ON ((budper.id = persec.section_id)))
				 LEFT JOIN cost_control_type jobtype ON ((bb.cost_control_type_id = jobtype.id)))
				 LEFT JOIN cost_control job ON ((bb.cost_control_id = job.id)))
				 LEFT JOIN res_partner partner ON ((bb.partner_id = partner.id)))
				 LEFT JOIN res_partner_category cat ON ((partner.category_id = cat.id)))
				 LEFT JOIN interface_account_entry ref_interface ON ((bb.document_ref_id = (ref_interface.id)::numeric)))
				 LEFT JOIN interface_system ref_system ON (((ref_interface.system_id)::numeric = (ref_system.id)::numeric)))
				 LEFT JOIN hr_expense_expense ref_hrexp ON ((bb.document_ref_id = (ref_hrexp.id)::numeric)))
				 LEFT JOIN issi_actual_ref_stock_picking_view ref_stock ON ((bb.document_ref_id = (ref_stock.stock_picking_id)::numeric)))
				 LEFT JOIN issi_actual_ref_invoice_view ref_invoice ON ((bb.document_ref_id = (ref_invoice.invoice_id)::numeric)))
				 LEFT JOIN hr_salary_expense ref_salary ON ((bb.document_ref_id = (ref_salary.id)::numeric)))
				 LEFT JOIN issi_hr_employee_view exp_hrreq ON ((ref_hrexp.employee_id = exp_hrreq.id)))
				 LEFT JOIN res_users exp_usrapp ON ((ref_hrexp.approver_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view exp_hrapp ON (((exp_usrapp.login)::text = (exp_hrapp.employee_code)::text)))
				 LEFT JOIN res_users interface_usrapp ON ((ref_interface.validate_user_id = interface_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view interface_hrapp ON (((interface_usrapp.login)::text = (interface_hrapp.employee_code)::text)))
				 LEFT JOIN res_users sal_usrreq ON ((ref_salary.submit_user_id = sal_usrreq.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrreq ON (((sal_usrreq.login)::text = (sal_hrreq.employee_code)::text)))
				 LEFT JOIN res_users sal_usrapp ON ((ref_salary.approve_user_id = exp_usrapp.id)))
				 LEFT JOIN issi_hr_employee_view sal_hrapp ON (((exp_usrapp.login)::text = (sal_hrapp.employee_code)::text)))
			  WHERE (("left"((act.code)::text, 1) = ANY (ARRAY['4'::text, '5'::text, '8'::text])) AND ("right"((perd.code)::text, 4) >= '2019'::text) AND (bb.amount <> (0)::numeric))
			  ORDER BY perd.code, act.code
        )
        """ % self._table)
