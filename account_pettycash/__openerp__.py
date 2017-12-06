# -*- coding: utf-8 -*-
{
    "name": "Petty Cash",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """
This module allow setting of petty cash holder / amount.
When user do expense request, user can request with the petty cash holder.
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
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/pettycash_view.xml',
        'views/hr_expense_view.xml',
    ],
}
