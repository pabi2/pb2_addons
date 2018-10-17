# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Account",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

* Account posting by selected tax branch
* All WHT account post go to a selected tax branch
* History of partner's bank account changes. Only user set in company config
  will have right to approve.
* Payment Type (cheque, transfer)

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
        "pabi_chartfield_merged",
        "pabi_account_move_document_ref",
        "hr_expense_auto_invoice",
        "pabi_source_document",
        "account_invoice_create_payment",
        "purchase_split_quote2order",
        "account_pettycash",
        "account_cancel_reversal",
        "pabi_interface",
        "account_debitnote",
    ],
    "data": [
        "data/default_value.xml",
        "security/security_group.xml",
        "security/ir.model.access.csv",
        "wizard/print_wht_cert_wizard.xml",
        "wizard/voucher_invoice_description_view.xml",
        "wizard/account_invoice_refund_view.xml",
        "wizard/account_debitnote_view.xml",
        "views/account_view.xml",
        "views/account_config.xml",
        "views/account_voucher_view.xml",
        "views/account_invoice_view.xml",
        "views/account_invoice_view.xml",
        "views/res_bank_view.xml",
        "views/res_partner_view.xml",
        "views/res_company_view.xml",
        "views/account_bank_receipt_view.xml",
    ],
}
