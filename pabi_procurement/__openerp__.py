# -*- coding: utf-8 -*-
# © 2015 TrinityRoots>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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
        "purchase_request_to_requisition",
        "purchase_split_quote2order",
        "purchase_requisition_operating_unit",
        "purchase_request_to_requisition_operating_unit",
        "purchase_operating_unit",
        "stock_operating_unit"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_request_line_make_purchase_requisition_view.xml",
        "wizard/cancel_reason_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "workflow/purchase_requisition_workflow.xml",
    ],
}
