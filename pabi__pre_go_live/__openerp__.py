# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Pre Go Live",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

* Allow create / duplicate purchase
* Allow create / import journal entries

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_procurement",
        "pabi_budget_plan",
        "pabi_invest_construction",
        "pabi_asset_management",
        "purchase_invoice_plan",
        "account",
    ],
    "data": [
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "views/purchase_request_view.xml",
        "views/hr_expense_view.xml",
        "views/invest_construction_view.xml",
        "views/asset_view.xml",
        "views/account_view.xml",
    ],
}
