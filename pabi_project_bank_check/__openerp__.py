# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Project's specific bank and balance check",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

Concept:
========

* Journal (payment method) can now be used for specific project.
* For normal case, Supplier Payment will show only
  Payment Method not tie to project
* For payment for a project with specific payment method, only show that.
* A journal (payment method) can be used for more than one project.
* A project can have more than one journal (payment method)

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_base",
        "pabi_account",
        "account_voucher",
    ],
    # Conflict on passing context to journal_id in account.voucher
    "conflicts": ["account_voucher_no_auto_lines"],
    "data": [
        "views/account_view.xml",
        "views/account_voucher_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
