# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Attachment Helper",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

This module add Attachment tab for

* HR Expense
* ???

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        # "document_url",
        "hr_expense",
    ],
    "data": [
        'wizard/open_attachment_url_view.xml',
        'views/hr_expense_view.xml',
    ],
}
