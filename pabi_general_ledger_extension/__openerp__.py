# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - General Ledger Extension",
    "summary": "",
    "version": "1.0",
    "category": "Human Resources",
    "description": """
Add ability to export General Ledger as xlsx
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Tharathip C.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_general_ledger_report",
        "pabi_utils",
    ],
    "data": [
        "wizard/export_balance_detail_wizard.xml",
        "xlsx_template/templates.xml",
        "xlsx_template/load_template.xml",
    ],
}
