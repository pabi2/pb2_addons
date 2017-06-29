# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Receivable Helper",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

This module group the receivable for ease of use,

* Advance Return
* Loan Late Payment Penalty
* Late Delivery Fine
* Retention

In future, there could be more.
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense_advance_clearing",
        "pabi_purchase_work_acceptance",
        "pabi_loan_receivable",
        "pabi_account_retention",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
}
