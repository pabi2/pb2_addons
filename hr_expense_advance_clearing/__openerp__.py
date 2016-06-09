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
        "hr_expense_auto_invoice",
    ],
    "data": [
        'data/product_data.xml',
        'views/expense_advance_view.xml',
        'views/invoice_view.xml',
    ],
}
