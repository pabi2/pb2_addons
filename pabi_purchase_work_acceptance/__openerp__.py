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
        "pabi_procurement",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/create_purchase_work_acceptance_view.xml",
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "views/purchase_work_acceptance_view.xml",
        "views/stock_view.xml",
        "data/ir.sequence.type.csv",
        "data/ir.sequence.csv",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
