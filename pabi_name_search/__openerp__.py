# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Name Search",
    "version": "1.0",
    "description": """

- All configuration for name_search in one place
- Extend search on invoice/payment/journal entry, i.e., PV001-PV005,PV006,PV007

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Ecosoft",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'pabi_base',
        'pabi_user_profile',
        'pabi_chartfield',
        'pabi_chartfield_merged',
        'pabi_asset_management',
        'pabi_budget_plan',
    ],
    "data": [
        'ir.model.csv',
    ],
}
