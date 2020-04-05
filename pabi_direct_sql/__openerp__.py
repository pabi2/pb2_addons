# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: Performance Tuning using Direct SQL",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

This module replace the use of ORM is some model to boost performance.

Activate it by system parameter,

- env['account.analytic.line'].create(), "pabi_direct_sql.analytic_create" = "True"

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'account',
        'account_budget_activity',
        'pabi_account_move_document_ref',
    ],
    "data": [
        'data/config_params.xml',
    ]
}
