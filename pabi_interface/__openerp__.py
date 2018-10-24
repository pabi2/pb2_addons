# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Interface from Other Systems",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

This moudule provide standard interface in generice way.

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "account_budget_activity",
        "pabi_chartfield",
        "l10n_th_account_tax_detail",
        "pabi_utils",
        # "pabi_account_move_adjustment",
    ],
    "data": [
        "data/interface_data.xml",
        "security/security_group.xml",
        "security/ir.model.access.csv",
        "views/interface_config_view.xml",
        "views/interface_account_view.xml",
        "views/account_view.xml",
    ],
}
