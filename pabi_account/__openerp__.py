# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Account",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

* Account posting by selected tax branch
* All WHT account post go to a selected tax branch

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "l10n_th_account",
        "l10n_th_account_tax_detail",
        "pabi_base",
        "pabi_chartfield",
        "account_move_line_doc_ref",
    ],
    "data": [
        "security/security_group.xml",
        "security/ir.model.access.csv",
        "views/account_config.xml",
        "views/account_voucher_view.xml",
        "views/account_invoice_view.xml",
        "views/voucher_payment_receipt_view.xml",
        "views/account_invoice_view.xml",
    ],
}
