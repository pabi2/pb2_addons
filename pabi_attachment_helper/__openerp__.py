# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Attachment Helper",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

This module add Attachment tab for

* HR Expense
* Payment Export

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        # "document_url",
        "hr_expense",
        'payment_export',
    ],
    "data": [
        'wizard/open_attachment_url_view.xml',
        'views/attachment_view.xml',
        'views/hr_expense_view.xml',
        'views/payment_export_view.xml',
    ],
}
