# -*- coding: utf-8 -*-
# © 2015 TrinityRoots>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Procurement Mockup",
    "summary": "Mock Up for procurement",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

PABI2 - Procurement Mock Up
==================================

  * Mock up fields for PABI2 procurement processes.

    """,
    "website": "https://nstda.or.th/",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_request_to_requisition",
    ],
    "data": [
        "views/purchase_request_view.xml"
    ],
}
