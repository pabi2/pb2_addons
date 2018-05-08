# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Debt Transfer",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

* Supplier master data, add new Debt Transfer (who to transfer debt to)
* In Supplier Payment, add new Transfer Debt To fields
* In Payment Export, choose partner form Transfer Debt To, if existss

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_account",
        "payment_export",
    ],
    "data": [
        "views/account_voucher_view.xml",
        "views/res_partner_view.xml",
    ],
}
