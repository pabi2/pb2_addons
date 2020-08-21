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
