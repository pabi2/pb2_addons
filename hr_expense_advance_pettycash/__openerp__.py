# -*- coding: utf-8 -*-
{
    "name": "HR Expense Petty Cash",
    "summary": "Advanc of type Petty Cash",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'hr_expense_advance_clearing',
    ],
    "data": [
        'data/hr_expense_data.xml',
        'views/hr_expense_view.xml',
        'views/hr_expense_view.xml',
    ],
}
