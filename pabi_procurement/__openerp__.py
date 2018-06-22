# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Procurement",
    "summary": "Pabi2 Procurement",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

PABI2 - Procurement Module
==================================

  * Add fields for PABI2 procurement processes.
  * Fix some functions from processes interaction


    """,
    "website": "https://nstda.or.th/",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_base",
        "pabi_web_config",
        "pabi_user_profile",
        "pabi_chartfield",
        "pabi_purchase_contract",
        "web_tree_many2one_clickable",
        "purchase_double_validation",
        "purchase_request_to_requisition",
        "purchase_split_quote2order",
        "purchase_invoice_plan",
        "purchase_split_requisition_line",
        "purchase_requisition_cancel_reason",
        "purchase_request_reject_reason",
        "purchase_force_done",
        "purchase_cancel_reason",
        "purchase_partial_invoicing",
        "purchase_partner_invoice_method",
        "l10n_th_thai_holidays",
        "l10n_th_amount_text_ext",
        "l10n_th_doctype_order",
        "res_partner_ext",
        "purchase_requisition_operating_unit",
        "purchase_request_to_requisition_operating_unit",
        "purchase_operating_unit",
        "account_budget_activity",
        "pabi_attachment_helper",
        "stock_request",
    ],
    "data": [
        "security/purchase_requisition.xml",
        "security/ir.model.access.csv",
        "wizard/purchase_request_line_make_purchase_requisition_view.xml",
        "wizard/reject_reason_view.xml",
        "wizard/purchase_requisition_partner_view.xml",
        "wizard/purchase_request_line_close_view.xml",
        "wizard/force_done_reason_view.xml",
        "wizard/accept_with_reason_wizard.xml",
        "views/purchase_request_view.xml",
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "views/product_view.xml",
        "views/partner_view.xml",
        "views/purchase_master_data_view.xml",
        "views/stock_request_view.xml",
        "workflow/purchase_requisition_workflow.xml",
        "workflow/purchase_workflow.xml",
        "data/pabiweb_config_parameter.xml",
        "data/pabi_purchase_sequence.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
