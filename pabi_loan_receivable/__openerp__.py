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
        "l10n_th_account",
        "sale_invoice_plan",
        'pabi_base',
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/loan_create_bank_invoice_wizard.xml",
        "wizards/loan_create_installment_order_wizard.xml",
        "views/res_config_view.xml",
        "views/loan_receivable_view.xml",
        "views/account_invoice_view.xml",
    ],
}
