# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Overwrite Due Date",
    "summary": "Allow overwrite due date in customer / supplier invoices",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

Account Invoice Overwrite Due Date
==================================

By standard, the invoice due date will always be suggested by payment term.
This is regardless of user specify the due date or not, when validated,
the suggested due date will be set.

This module will change this behaviour by,

* If no due date is specified during invoice draft, once validated,
  the due date will be set (same as standard).
* If due date is specified during invoice draft, once validated,
  the specified due date will be used (system suggesting won't be used)
* For invoice with state = Open, the due date is still editable.
* For invoice with state = Paid, the due date is readonly

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "demo": [
        "demo/account_invoice_demo.xml"
    ]
}
