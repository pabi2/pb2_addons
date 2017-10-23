# -*- coding: utf-8 -*-
{
    "name": "PABI2 :: Petty Cash",
    "summary": "",
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
        'pabi_account',
        'pabi_hr_expense',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/pettycash_view.xml',
        'views/hr_expense_view.xml',
    ],
}
