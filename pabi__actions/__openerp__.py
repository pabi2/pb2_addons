# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Actions / Jobs for Automation",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

* [hr.expense].action_accept_to_paid

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_hr_expense",
        "account_invoice_create_payment",
    ],
    "data": [
        "data/server_action.xml",
    ],
}
