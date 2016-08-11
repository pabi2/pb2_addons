# -*- coding: utf-8 -*-
{
    "name": "Base Payment Export",
    "version": "8.0.0.1.0",
    "license": 'AGPL-3',
    "author": "Ecosoft",
    "category": "Accounting & Finance",
    "depends": [
        "base",
        "document",
    ],
    "description": """

    """,
    "data": [
        'security/ir.model.access.csv',
        'wizard/export_parser_view.xml',
        "views/payment_export_config_view.xml",
    ],
    'installable': True,
}
