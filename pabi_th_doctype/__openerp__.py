# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sequence Number by Document Type",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

PABI2 Extension to l10n_th_doctype for,

* Work Acceptance
* Approval Report
* Stock Request
* Stock Transfer
* Stock Borrow
* Payment Export
* Bank Receipt
* Interface Account

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'l10n_th_doctype',
        'pabi_purchase_work_acceptance',
        'stock_request',
        'pabi_procurement',
        'payment_export',
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/doctype_data.xml",
    ],
}
