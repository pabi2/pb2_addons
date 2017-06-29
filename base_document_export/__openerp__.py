# -*- coding: utf-8 -*-
{
    "name": "Base Document Export",
    "version": "8.0.0.1.0",
    "license": 'AGPL-3',
    "author": "Ecosoft",
    "category": "Accounting & Finance",
    "depends": [
        "base",
        "document",
        "account",
    ],
    "description": """

    """,
    "data": [
        'security/ir.model.access.csv',
        'wizard/export_parser_view.xml',
        "views/document_export_config_view.xml",
        "views/account_view.xml",
    ],
    'installable': True,
}
