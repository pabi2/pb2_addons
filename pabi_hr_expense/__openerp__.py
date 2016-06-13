# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - HR Expense (AP/AV)",
    "summary": "",
    "version": "1.0",
    "category": "Human Resources",
    "description": """

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense_auto_invoice",
        "account_budget_activity",
        "pabi_bank",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/hr_expense_change_advance_date_due_view.xml",
        "views/account_activity_view.xml",
        "views/hr_expense_view.xml",
    ],
}
