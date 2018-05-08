# -*- coding: utf-8 -*-
{
    "name": "HR Expense Advance Clearing",
    "summary": "HR Expense Advance Clearing.",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

HR Expense Advance Clearing
============================

HR Expense Advance Clearing

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense_sequence",
        "hr_expense_auto_invoice",
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/hr_expense_data.xml',
        'data/invoice_workflow.xml',
        'views/account_config.xml',
        'views/hr_expense_view.xml',
        'views/account_invoice_view.xml',
    ],
}
