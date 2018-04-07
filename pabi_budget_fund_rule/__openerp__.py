# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Budget Fund Rule",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

Additional validation logics for Fund vs Project.

For example,

* Only some activity groups allowed

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_base",
        "pabi_chartfield",
        "pabi_budget_monitor",
        "pabi_my_project",  # because we need menu to be under myProject
        "pabi_utils",
    ],
    "data": [
        "data/fund_rule_data.xml",
        "data/budget_fund_rule_sequence.xml",
        "security/ir.model.access.csv",
        "views/budget_fund_rule_view.xml",
    ],
}
