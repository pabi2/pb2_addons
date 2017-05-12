# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - myProject Master / Interface",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        "pabi_base",
        "account_budget_activity",
        "document_status_history",
    ],
    "data": [
        "data/project_history_rule.xml",
        "security/ir.model.access.csv",
        "views/res_project_view.xml",
    ],
    "application": False,
    "installable": True,
}
