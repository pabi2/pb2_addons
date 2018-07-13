# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Docline Seq",
    "summary": "",
    "version": "1.0",
    "category": "Hidden",
    "description": """
This module add new docline_seq to account.invoice.line
The seq will be set only when document is confirmed.

In case you want to recalculate all document lines,
* Set document_seq = 0
* Upgrade this module
    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'account',
    ],
    "data": [
        'views/account_invoice_view.xml',
    ],
    "application": False,
    "installable": True,
}
