# -*- coding: utf-8 -*-
{
    "name": "HR Expense with auto invoice",
    "summary": "Auto create supplier invoice instead of expense journal.",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

HR Expense with auto invoice
============================

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense",
    ],
    "data": [
        "views/hr_expense_view.xml",
    ],
}
