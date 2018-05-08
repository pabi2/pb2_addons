# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Source Document",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """
It stores very first origin document reference on invoice.
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'account',
        'sale',
        'purchase',
        'pabi_purchase_work_acceptance',
        'hr_expense_auto_invoice',
        'purchase_invoice_plan',
        'sale_invoice_plan',
    ],
    "data": [
        'views/account_invoice_view.xml',
    ],
}
