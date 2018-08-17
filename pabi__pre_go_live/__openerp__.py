# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Pre Go Live",
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
        "pabi_budget_plan",
    ],
    "data": [
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "views/purchase_request_view.xml",
        "views/hr_expense_view.xml",
    ],
}
