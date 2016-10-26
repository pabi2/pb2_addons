# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Retention and Retention Clearing",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

This module do 2 things,

1) On Customer Invoice,

* Adds new receivable type "Retention" in relation with a purcase order.

2) On Supplier invoice

* Allow clearing the retention amount that related to a purchase order, both,

** Customer Invoice from (1)
** Retaintion based on Invoice Plan feature

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_invoice_plan",
        "pabi_account",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
}
