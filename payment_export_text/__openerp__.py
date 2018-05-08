# -*- coding: utf-8 -*-
{
    "name": "Payment Export Pack - Text",
    "version": "8.0.0.1.0",
    "license": 'AGPL-3',
    "author": "Ecosoft",
    "category": "Accounting & Finance",
    "depends": [
        "payment_export",
        'base_document_export'
    ],
    "description": """
Export payment in text file.
    """,
    "data": [
        # 'export_view.xml',
        'views/payment_export_view.xml',
    ],
    'installable': True,
}
