# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Interface to JE",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

This moudule provide standard interface in generice way.

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "account_budget_activity",
        "pabi_chartfield",
    ],
    "data": [
        "data/system_origin_data.xml",
        "security/security_group.xml",
        "security/ir.model.access.csv",
        "views/account_interface_view.xml",
        "views/system_origin_view.xml",
    ],
}
