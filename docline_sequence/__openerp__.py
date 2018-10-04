# -*- coding: utf-8 -*-
{
    "name": "Document Line Sequence",
    "summary": "",
    "version": "1.0",
    "category": "Hidden",
    "description": """
This module add new docline_seq to sale/purchase/invoice lines
The seq will be set on line changes.

In case you want to recalculate all document lines,

  * Set document_seq = 0
  * Upgrade this module
    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'account',
        'sale',
        'purchase',
        'hr_expense',
        'purchase_request',
    ],
    "data": [
        'views/account_invoice_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    "application": False,
    "installable": True,
}
