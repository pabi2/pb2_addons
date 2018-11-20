# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Purchase Work Acceptance",
    "summary": "Pabi2 Procurement",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

PABI2 - Purchase Work Acceptance
================================

  * Manage PABI2 purchase work acceptance module.
  * Manage fine condition on PO
  * Calculate Fine in work acceptance form.
  * Rate Supplier shipment.


    """,
    "website": "https://nstda.or.th/",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "purchase_cash_on_delivery",
        "pabi_procurement",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/po_line_invoice_view.xml",
        "wizard/create_purchase_work_acceptance_view.xml",
        "views/account_config.xml",
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "views/purchase_work_acceptance_view.xml",
        "views/stock_view.xml",
        "views/account_invoice_view.xml",
        "views/work_acceptance_config.xml",
        "data/pabi_work_acceptance_sequence.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
