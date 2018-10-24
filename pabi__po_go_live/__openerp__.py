# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - PO Go Live",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

* Allow create / duplicate purchase

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_procurement",
        "purchase_invoice_plan",
    ],
    "data": [
        "views/purchase_view.xml",
    ],
}
