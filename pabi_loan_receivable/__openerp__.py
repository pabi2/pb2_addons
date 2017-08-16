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
        'mass_editing',
    ],
    "data": [
        "data/product_data.xml",
        "data/loan_agreement_section_mass_editing_data.xml",
        "security/ir.model.access.csv",
        "wizards/loan_create_bank_invoice_wizard.xml",
        "wizards/loan_create_installment_order_wizard.xml",
        "wizards/update_section_view.xml",
        "views/account_config.xml",
        "views/loan_receivable_view.xml",
        "views/account_invoice_view.xml",
    ],
}
