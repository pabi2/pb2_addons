# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Name Search",
    "version": "1.0",
    "description": """

All configuration for name_search in one place

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
        'base_name_search_improved',
    ],
    "data": [
        'ir.model.csv',
    ],
}
