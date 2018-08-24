# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Purchase Billing",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """
This document is used to confirm the new invoice due date.
Choose supplier invoice you want to group in this billing document.
As this document is confirmed,
the invoice date and due date be set for all selected documents.

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_purchase_work_acceptance",
        "pabi_forms",
        "purchase_cash_on_delivery",
        "pabi_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/purchase_billing_email_template.xml",
        "data/purchase_billing_sequence.xml",
        "views/purchase_billing_view.xml",
        "views/account_invoice_view.xml",
        "views/account_config.xml",
        "views/billing_date.xml",
    ],
}
