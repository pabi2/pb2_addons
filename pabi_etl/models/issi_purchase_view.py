# -*- coding: utf-8 -*-
from openerp import models
from openerp import tools


class etl_issi_purchase_tracking(models.Model):
    _name = 'etl.issi.purchase.tracking'
    _auto = False
    _description = 'Purchase Tracking'

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
		 SELECT aa.pr_id,
			aa.po_id,
			aa.inv_name,
			aa.vou_name,
			aa.org_id,
			aa.org,
			aa.create_date,
			aa.request_ref,
			aa.pr_status,
			aa.req_employee_id,
			aa.request_by,
			aa.preparer_id,
			aa.preparer,
			aa.approved_date,
			aa.res_person_pr_id,
			aa.res_person_pr,
			aa.pr_approved_date,
			aa.objective,
			aa.amount_thb,
			aa.pr_source_budget,
				CASE
					WHEN aa.pr_source_budget = 'unit_base'::text THEN pr_section.source_budget
					WHEN aa.pr_source_budget = 'invest_construction'::text THEN pr_construction.source_budget
					WHEN aa.pr_source_budget = 'project_base'::text THEN pr_project.source_budget
					WHEN aa.pr_source_budget = 'invest_asset'::text THEN pr_asset.source_budget
					WHEN aa.pr_source_budget = 'personnel'::text THEN pr_personnel.source_budget
					ELSE ''::character varying
				END AS pr_source_budget_code,
				CASE
					WHEN aa.pr_source_budget = 'unit_base'::text THEN pr_section.source_budget_name
					WHEN aa.pr_source_budget = 'invest_construction'::text THEN pr_construction.source_budget_name
					WHEN aa.pr_source_budget = 'project_base'::text THEN pr_project.source_budget_name
					WHEN aa.pr_source_budget = 'invest_asset'::text THEN pr_asset.source_budget_name
					WHEN aa.pr_source_budget = 'personnel'::text THEN pr_personnel.source_budget_name
					ELSE ''::text
				END AS pr_source_budget_name,
			aa.bidding_ref,
			aa.bidding_date,
			aa.bidding_approved_date,
			aa.ordersss,
			aa.order_ref,
			aa.order_date,
			aa.contract_start_date,
			aa.contract_end_date,
			aa.contract_no,
			aa.po_contract_start_date,
			aa.po_contract_end_date,
			aa.supplier_id,
			aa.supplier,
			aa.supplier_payment_term,
			aa.seq,
			aa.product,
			aa.description,
			aa.scheduled_date,
			aa.po_source_budget,
				CASE
					WHEN aa.po_source_budget = 'unit_base'::text THEN po_section.source_budget
					WHEN aa.po_source_budget = 'invest_construction'::text THEN po_construction.source_budget
					WHEN aa.po_source_budget = 'project_base'::text THEN po_project.source_budget
					WHEN aa.po_source_budget = 'invest_asset'::text THEN po_asset.source_budget
					WHEN aa.po_source_budget = 'personnel'::text THEN po_personnel.source_budget
					ELSE ''::character varying
				END AS po_source_budget_code,
				CASE
					WHEN aa.po_source_budget = 'unit_base'::text THEN po_section.source_budget_name
					WHEN aa.po_source_budget = 'invest_construction'::text THEN po_construction.source_budget_name
					WHEN aa.po_source_budget = 'project_base'::text THEN po_project.source_budget_name
					WHEN aa.po_source_budget = 'invest_asset'::text THEN po_asset.source_budget_name
					WHEN aa.po_source_budget = 'personnel'::text THEN po_personnel.source_budget_name
					ELSE ''::text
				END AS po_source_budget_name,
			aa.fund,
			aa.job_order,
			aa.quantity,
			aa.uom,
			aa.unit_price,
			aa.sub_total,
			aa.currency,
			aa.fiscal_year,
			aa.res_person_po_id,
			aa.res_person_po,
			aa.payment_term_po,
			aa.acceptance_no,
			aa.in_no,
			aa.acceptance_date,
			aa.invoice_no,
			aa.invoice_date,
			aa.receive_date,
			aa.billing_no,
			aa.billing_date,
			aa.billing_sent_date,
			aa.billing_receipt_date,
			aa.journal_entry_kv,
			aa.validate_date,
			aa.validate_by_id,
			aa.validate_by,
			aa.journal_entry_pv,
			aa.payment_date,
			aa.payment_type,
			aa.transfer_date,
			aa.import_date,
			aa.po_status,
			aa.po_close,
			aa.acceptance_status,
			aa.billing_status,
			aa.journal_kv_status,
			aa.pd_method,
			aa.condition_detail,
			aa.wa_create_date
		   FROM ( SELECT pr.id AS pr_id,
					po.id AS po_id,
					inv.name AS inv_name,
					vou.name AS vou_name,
					org.code AS org_id,
					ou.name AS org,
					pr.date_start AS create_date,
					pr.name AS request_ref,
					pr.state AS pr_status,
					part.employee_code AS req_employee_id,
					part.full_name_th AS request_by,
					''::text AS preparer_id,
					''::text AS preparer,
					pr.date_approve AS approved_date,
					pr_respon.employee_code AS res_person_pr_id,
					pr_respon.full_name_th AS res_person_pr,
					''::text AS pr_approved_date,
					pr.objective,
					prl.price_subtotal AS amount_thb,
						CASE
							WHEN prl.section_id IS NOT NULL THEN 'unit_base'::text
							WHEN prl.invest_construction_phase_id IS NOT NULL THEN 'invest_construction'::text
							WHEN prl.project_id IS NOT NULL THEN 'project_base'::text
							WHEN prl.invest_asset_id IS NOT NULL THEN 'invest_asset'::text
							WHEN prl.personnel_costcenter_id IS NOT NULL THEN 'personnel'::text
							ELSE ''::text
						END AS pr_source_budget,
					prl.section_id AS pr_section_id,
					prl.invest_construction_phase_id AS pr_invest_construction_phase_id,
					prl.project_id AS pr_project_id,
					prl.invest_asset_id AS pr_invest_asset_id,
					prl.personnel_costcenter_id AS pr_personnel_costcenter_id,
					pd.name AS bidding_ref,
					pd.ordering_date AS bidding_date,
					pd.date_doc_approve AS bidding_approved_date,
					pcd.name AS condition_detail,
					po.name AS ordersss,
					po.name AS order_ref,
					po.date_order AS order_date,
					po.date_contract_start AS contract_start_date,
					po.date_contract_end AS contract_end_date,
					poc.display_code AS contract_no,
					poc.start_date AS po_contract_start_date,
					poc.end_date AS po_contract_end_date,
					part_po.search_key AS supplier_id,
					part_po.display_name2 AS supplier,
					pay.name AS supplier_payment_term,
					pol.docline_seq AS seq,
					prod.name_template AS product,
					pol.name AS description,
					pol.date_planned AS scheduled_date,
						CASE
							WHEN pol.section_id IS NOT NULL THEN 'unit_base'::text
							WHEN pol.invest_construction_phase_id IS NOT NULL THEN 'invest_construction'::text
							WHEN pol.project_id IS NOT NULL THEN 'project_base'::text
							WHEN pol.invest_asset_id IS NOT NULL THEN 'invest_asset'::text
							WHEN pol.personnel_costcenter_id IS NOT NULL THEN 'personnel'::text
							ELSE ''::text
						END AS po_source_budget,
					pol.section_id AS po_section_id,
					pol.invest_construction_phase_id AS po_invest_construction_phase_id,
					pol.project_id AS po_project_id,
					pol.invest_asset_id AS po_invest_asset_id,
					pol.personnel_costcenter_id AS po_personnel_costcenter_id,
					fund_po.name AS fund,
					cost_po.name AS job_order,
					pol.product_qty AS quantity,
					uom.name AS uom,
					pol.price_unit AS unit_price,
					pol.price_unit * pol.product_qty AS sub_total,
					cur.name AS currency,
					fis.name AS fiscal_year,
					po_respon.employee_code AS res_person_po_id,
					po_respon.full_name_th AS res_person_po,
					pay.name AS payment_term_po,
					pwa.name AS acceptance_no,
					sp.name AS in_no,
					pwa.date_accept AS acceptance_date,
					pwa.supplier_invoice AS invoice_no,
					pwa.date_invoice AS invoice_date,
					pwa.date_receive AS receive_date,
					pb.name AS billing_no,
					pb.date AS billing_date,
					pb.date_sent AS billing_sent_date,
					inv.date_receipt_billing AS billing_receipt_date,
					inv.number AS journal_entry_kv,
					inv.date_invoice AS validate_date,
					inv_part.employee_code AS validate_by_id,
					inv_part.full_name_th AS validate_by,
					vou.number AS journal_entry_pv,
					vou.date AS payment_date,
					inv.payment_type,
					vou.date_value AS transfer_date,
					now() AS import_date,
						CASE
							WHEN po.state::text = 'draft'::text THEN 'Draft'::text
							WHEN po.state::text = 'sent'::text THEN 'RFQ'::text
							WHEN po.state::text = 'bid'::text THEN 'Bid Received'::text
							WHEN po.state::text = 'confirmed'::text THEN 'Waiting to Release'::text
							WHEN po.state::text = 'approved'::text THEN 'PO Released'::text
							WHEN po.state::text = 'except_picking'::text THEN 'Shipping Exception'::text
							WHEN po.state::text = 'except_invoice'::text THEN 'Invoice Exception'::text
							WHEN po.state::text = 'done'::text THEN 'Done'::text
							WHEN po.state::text = 'cancel'::text THEN 'Cancelled'::text
							ELSE NULL::text
						END AS po_status,
						CASE
							WHEN po.technical_closed = true THEN 1
							WHEN po.technical_closed = false THEN 0
							ELSE NULL::integer
						END AS po_close,
					pwa.state AS acceptance_status,
					pb.state AS billing_status,
					inv.state AS journal_kv_status,
					pdmethod.name AS pd_method,
					pwa.create_date as wa_create_date
				   FROM purchase_request pr
					 LEFT JOIN purchase_request_line prl ON prl.request_id = pr.id
					 LEFT JOIN purchase_request_purchase_requisition_line_rel prpdrel ON prpdrel.purchase_request_line_id = prl.id
					 LEFT JOIN purchase_requisition_line pdl ON prpdrel.purchase_requisition_line_id = pdl.id
					 LEFT JOIN purchase_requisition pd ON pd.id = pdl.requisition_id
					 LEFT JOIN purchase_method pdmethod ON pd.purchase_method_id = pdmethod.id
					 LEFT JOIN purchase_condition_detail pcd ON pcd.id = pd.purchase_condition_detail_id
					 LEFT JOIN purchase_contract poc ON poc.requisition_id = pd.id
					 LEFT JOIN purchase_order po ON po.requisition_id = pd.id
					 LEFT JOIN purchase_order_line pol ON pol.requisition_line_id = pdl.id
					 LEFT JOIN purchase_work_acceptance pwa ON pwa.order_id = po.id
					 LEFT JOIN cost_control cost_po ON cost_po.id = pol.cost_control_id
					 LEFT JOIN res_currency cur ON cur.id = po.currency_id
					 LEFT JOIN account_fiscalyear fis ON fis.id = pol.fiscalyear_id
					 LEFT JOIN res_fund fund_po ON fund_po.id = pol.fund_id
					 LEFT JOIN res_partner part_po ON part_po.id = po.partner_id
					 LEFT JOIN res_users pr_res ON pr_res.id = pr.responsible_uid
					 LEFT JOIN issi_hr_employee_view pr_respon ON pr_respon.employee_code::text = pr_res.login::text
					 LEFT JOIN res_users po_res ON po_res.id = po.responsible_uid
					 LEFT JOIN issi_hr_employee_view po_respon ON po_respon.employee_code::text = po_res.login::text
					 LEFT JOIN res_users users ON users.id = pr.requested_by
					 LEFT JOIN issi_hr_employee_view part ON part.employee_code::text = users.login::text
					 LEFT JOIN stock_picking sp ON sp.acceptance_id = pwa.id
					 LEFT JOIN account_invoice inv ON inv.source_document::text = po.name::text
					 LEFT JOIN res_users inv_users ON inv_users.id = inv.validate_user_id
					 LEFT JOIN issi_hr_employee_view inv_part ON inv_part.employee_code::text = inv_users.login::text
					 LEFT JOIN account_invoice_line invl ON invl.invoice_id = inv.id
					 LEFT JOIN purchase_billing pb ON pb.id = inv.purchase_billing_id
					 LEFT JOIN account_voucher_line voul ON voul.invoice_id = inv.id
					 LEFT JOIN account_voucher vou ON vou.id = voul.voucher_id
					 LEFT JOIN product_product prod ON prod.id = pol.product_id
					 LEFT JOIN product_uom uom ON uom.id = pol.product_uom
					 LEFT JOIN account_payment_term pay ON pay.id = po.payment_term_id
					 LEFT JOIN operating_unit ou ON ou.id = pr.operating_unit_id OR ou.id = po.operating_unit_id
					 LEFT JOIN res_org org ON org.id = ou.org_id
				  WHERE (pol.id IS NULL OR pol.state::text <> 'cancel'::text) AND (po.id IS NULL OR po.name::text !~~ 'RFQ%%'::text)
				UNION
				 SELECT pr.id AS pr_id,
					po.id AS po_id,
					inv.name AS inv_name,
					vou.name AS vou_name,
					org.code AS org_id,
					ou.name AS org,
					pr.date_start AS create_date,
					pr.name AS request_ref,
					pr.state AS pr_status,
					part.employee_code AS req_employee_id,
					part.full_name_th AS request_by,
					''::text AS preparer_id,
					''::text AS preparer,
					pr.date_approve AS approved_date,
					pr_respon.employee_code AS res_person_pr_id,
					pr_respon.full_name_th AS res_person_pr,
					''::text AS pr_approved_date,
					pr.objective,
					prl.price_subtotal AS amount_thb,
						CASE
							WHEN prl.section_id IS NOT NULL THEN 'unit_base'::text
							WHEN prl.invest_construction_phase_id IS NOT NULL THEN 'invest_construction'::text
							WHEN prl.project_id IS NOT NULL THEN 'project_base'::text
							WHEN prl.invest_asset_id IS NOT NULL THEN 'invest_asset'::text
							WHEN prl.personnel_costcenter_id IS NOT NULL THEN 'personnel'::text
							ELSE ''::text
						END AS pr_source_budget,
					prl.section_id AS pr_section_id,
					prl.invest_construction_phase_id AS pr_invest_construction_phase_id,
					prl.project_id AS pr_project_id,
					prl.invest_asset_id AS pr_invest_asset_id,
					prl.personnel_costcenter_id AS pr_personnel_costcenter_id,
					pd.name AS bidding_ref,
					pd.ordering_date AS bidding_date,
					pd.date_doc_approve AS bidding_approved_date,
					pcd.name AS condition_detail,
					po.name AS ordersss,
					po.name AS order_ref,
					po.date_order AS order_date,
					po.date_contract_start AS contract_start_date,
					po.date_contract_end AS contract_end_date,
					poc.display_code AS contract_no,
					poc.start_date AS po_contract_start_date,
					poc.end_date AS po_contract_end_date,
					part_po.search_key AS supplier_id,
					part_po.display_name2 AS supplier,
					pay.name AS supplier_payment_term,
					pol.docline_seq AS seq,
					prod.name_template AS product,
					pol.name AS description,
					pol.date_planned AS scheduled_date,
						CASE
							WHEN pol.section_id IS NOT NULL THEN 'unit_base'::text
							WHEN pol.invest_construction_phase_id IS NOT NULL THEN 'invest_construction'::text
							WHEN pol.project_id IS NOT NULL THEN 'project_base'::text
							WHEN pol.invest_asset_id IS NOT NULL THEN 'invest_asset'::text
							WHEN pol.personnel_costcenter_id IS NOT NULL THEN 'personnel'::text
							ELSE ''::text
						END AS po_source_budget,
					pol.section_id AS po_section_id,
					pol.invest_construction_phase_id AS po_invest_construction_phase_id,
					pol.project_id AS po_project_id,
					pol.invest_asset_id AS po_invest_asset_id,
					pol.personnel_costcenter_id AS po_personnel_costcenter_id,
					fund_po.name AS fund,
					cost_po.name AS job_order,
					pol.product_qty AS quantity,
					uom.name AS uom,
					pol.price_unit AS unit_price,
					pol.price_unit * pol.product_qty AS sub_total,
					cur.name AS currency,
					fis.name AS fiscal_year,
					po_respon.employee_code AS res_person_po_id,
					po_respon.full_name_th AS res_person_po,
					pay.name AS payment_term_po,
					pwa.name AS acceptance_no,
					sp.name AS in_no,
					pwa.date_accept AS acceptance_date,
					pwa.supplier_invoice AS invoice_no,
					pwa.date_invoice AS invoice_date,
					pwa.date_receive AS receive_date,
					pb.name AS billing_no,
					pb.date AS billing_date,
					pb.date_sent AS billing_sent_date,
					inv.date_receipt_billing AS billing_receipt_date,
					inv.number AS journal_entry_kv,
					inv.date_invoice AS validate_date,
					inv_part.employee_code AS validate_by_id,
					inv_part.full_name_th AS validate_by,
					vou.number AS journal_entry_pv,
					vou.date AS payment_date,
					inv.payment_type,
					vou.date_value AS transfer_date,
					now() AS import_date,
						CASE
							WHEN po.state::text = 'draft'::text THEN 'Draft'::text
							WHEN po.state::text = 'sent'::text THEN 'RFQ'::text
							WHEN po.state::text = 'bid'::text THEN 'Bid Received'::text
							WHEN po.state::text = 'confirmed'::text THEN 'Waiting to Release'::text
							WHEN po.state::text = 'approved'::text THEN 'PO Released'::text
							WHEN po.state::text = 'except_picking'::text THEN 'Shipping Exception'::text
							WHEN po.state::text = 'except_invoice'::text THEN 'Invoice Exception'::text
							WHEN po.state::text = 'done'::text THEN 'Done'::text
							WHEN po.state::text = 'cancel'::text THEN 'Cancelled'::text
							ELSE NULL::text
						END AS po_status,
						CASE
							WHEN po.technical_closed = true THEN 1
							WHEN po.technical_closed = false THEN 0
							ELSE NULL::integer
						END AS po_close,
					pwa.state AS acceptance_status,
					pb.state AS billing_status,
					inv.state AS journal_kv_status,
					pdmethod.name AS pd_method,
					pwa.create_date as wa_create_date
				   FROM purchase_order po
					 LEFT JOIN purchase_requisition pd ON pd.id = po.requisition_id
					 LEFT JOIN purchase_method pdmethod ON pd.purchase_method_id = pdmethod.id
					 LEFT JOIN purchase_contract poc ON poc.requisition_id = pd.id
					 LEFT JOIN purchase_condition_detail pcd ON pcd.id = pd.purchase_condition_detail_id
					 LEFT JOIN purchase_order_line pol ON pol.order_id = po.id
					 LEFT JOIN purchase_requisition_line pdl ON pdl.id = pol.requisition_line_id
					 LEFT JOIN purchase_request_purchase_requisition_line_rel prpdrel ON prpdrel.purchase_requisition_line_id = pdl.id
					 LEFT JOIN purchase_request_line prl ON prl.id = prpdrel.purchase_request_line_id
					 LEFT JOIN purchase_request pr ON pr.id = prl.request_id
					 LEFT JOIN purchase_work_acceptance pwa ON pwa.order_id = po.id
					 LEFT JOIN cost_control cost_po ON cost_po.id = pol.cost_control_id
					 LEFT JOIN res_currency cur ON cur.id = po.currency_id
					 LEFT JOIN account_fiscalyear fis ON fis.id = pol.fiscalyear_id
					 LEFT JOIN res_fund fund_po ON fund_po.id = pol.fund_id
					 LEFT JOIN res_partner part_po ON part_po.id = po.partner_id
					 LEFT JOIN res_users pr_res ON pr_res.id = pr.responsible_uid
					 LEFT JOIN issi_hr_employee_view pr_respon ON pr_respon.employee_code::text = pr_res.login::text
					 LEFT JOIN res_users po_res ON po_res.id = po.responsible_uid
					 LEFT JOIN issi_hr_employee_view po_respon ON po_respon.employee_code::text = po_res.login::text
					 LEFT JOIN res_users users ON users.id = pr.requested_by
					 LEFT JOIN issi_hr_employee_view part ON part.employee_code::text = users.login::text
					 LEFT JOIN stock_picking sp ON sp.acceptance_id = pwa.id
					 LEFT JOIN account_invoice inv ON inv.source_document::text = po.name::text
					 LEFT JOIN res_users inv_users ON inv_users.id = inv.user_id
					 LEFT JOIN issi_hr_employee_view inv_part ON inv_part.employee_code::text = inv_users.login::text
					 LEFT JOIN account_invoice_line invl ON invl.invoice_id = inv.id
					 LEFT JOIN purchase_billing pb ON pb.id = inv.purchase_billing_id
					 LEFT JOIN account_voucher_line voul ON voul.invoice_id = inv.id
					 LEFT JOIN account_voucher vou ON vou.id = voul.voucher_id
					 LEFT JOIN product_product prod ON prod.id = pol.product_id
					 LEFT JOIN product_uom uom ON uom.id = pol.product_uom
					 LEFT JOIN account_payment_term pay ON pay.id = po.payment_term_id
					 LEFT JOIN operating_unit ou ON ou.id = pr.operating_unit_id OR ou.id = po.operating_unit_id
					 LEFT JOIN res_org org ON org.id = ou.org_id
				  WHERE pol.state::text <> 'cancel'::text AND po.name::text !~~ 'RFQ%%'::text AND pr.id IS NULL) aa
			 LEFT JOIN issi_m_source_budget_view pr_section ON aa.pr_section_id = pr_section.section_id
			 LEFT JOIN issi_m_source_budget_view pr_project ON aa.pr_project_id = pr_project.project_id
			 LEFT JOIN issi_m_source_budget_view pr_asset ON aa.pr_invest_asset_id = pr_asset.invest_asset_id
			 LEFT JOIN issi_m_source_budget_view pr_construction ON aa.pr_invest_construction_phase_id = pr_construction.invest_construction_phase_id
			 LEFT JOIN issi_m_source_budget_view pr_personnel ON aa.pr_personnel_costcenter_id = pr_personnel.personnel_costcenter_id
			 LEFT JOIN issi_m_source_budget_view po_section ON aa.po_section_id = po_section.section_id
			 LEFT JOIN issi_m_source_budget_view po_project ON aa.po_project_id = po_project.project_id
			 LEFT JOIN issi_m_source_budget_view po_asset ON aa.po_invest_asset_id = po_asset.invest_asset_id
			 LEFT JOIN issi_m_source_budget_view po_construction ON aa.po_invest_construction_phase_id = po_construction.invest_construction_phase_id
			 LEFT JOIN issi_m_source_budget_view po_personnel ON aa.po_personnel_costcenter_id = po_personnel.personnel_costcenter_id
        )
        """ % self._table)
