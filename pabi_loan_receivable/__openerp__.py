# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Loan Receivable",
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
        "account",
        "account_voucher",
        "sale_invoice_plan",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/loan_create_bank_invoice_wizard.xml",
        "views/loan_receivable_view.xml",
    ],
}
