# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Retention and Retention Clearing",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

When a PO is issues, there are possible 2 kind of retentions,

1) Contract Warranty Retention: where NSTDA, at the begin of a purchase
(or a project), Customer Invoice of receivable type = Supplier Retention
will be issued.

2) Retention from PO's Supplier Invoice Plan: where retention is deduct
from each supplier invoice.

After time gone by, and it is time to return these retained money back to
supplier, NSTDA by accountant, can create new Supplier Invoice and refer back
to the PO and retrieve the above 2 kind of retentions.

A new checkbox and PO selection will display all Purchase Order which are,

* Belong to a Partner
* Has amount retained, either in (1) or (2)
* Has not been returned yet

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
