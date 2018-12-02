# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Purchase Order Revision",
    "summary": "Pabi2 Purchase Order Revision",
    "version": "8.0.1.0.0",
    "category": "Stock",
    "description": """

PABI2 - Purchase Order Revision
===============================

  * Create revision from purchase order which has done state

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
        "views/purchase_view.xml"
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
