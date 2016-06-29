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
        "hr_expense_cancel_reason",
        "account_budget_activity",
        "pabi_bank",
    ],
    "data": [
        "security/ir.model.access.csv",
        'wizard/expense_create_multi_supplier_invoice_view.xml',
        "wizard/hr_expense_change_advance_date_due_view.xml",
        "views/account_activity_view.xml",
        "views/hr_expense_view.xml",
        'wizard/expense_create_supplier_invoice_view.xml',
    ],
}
