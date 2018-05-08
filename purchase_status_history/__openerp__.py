# -*- coding: utf-8 -*-

{
    'name': 'Purchase Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of purchase order.
    """,
    'depends': [
        'document_status_history',
        'purchase',
    ],
    'demo': [],
    'data': [
        'data/purchase_history_rule.xml',
        'views/purchase_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
