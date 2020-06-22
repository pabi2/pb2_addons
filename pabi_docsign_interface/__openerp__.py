# -*- coding: utf-8 -*-
# © 2020 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "NSTDA :: PABI2 - Docsign Interface",
    "summary": "Send data dict to docsign server",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """
        create new wizard for send data to server printting eTax
    """,
    "website": "http://ecosoft.co.th",
    "author": "Saran Lim.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["pabi_forms"],
    "data": [
        # "wizard/etax_invoice_wizard.xml",
        # "wizard/etax_update_invoice_wizard.xml",
        "views/pabi_web_config.xml",
        "views/account_invoice_view.xml",
        "views/account_voucher_view.xml",
        "print_account_voucher/print_account_voucher_wizard.xml",
    ],
}
