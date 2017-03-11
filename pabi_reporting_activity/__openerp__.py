# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Reporting Activity",
    "summary": "Add new dimension for reporting purpose",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """
TODO:

* Add new dimension, reporting activity in all documents
* If activity_id has value, this one should be the same
* If activity_id don't have value, user can select it

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_budget_activity",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
}
