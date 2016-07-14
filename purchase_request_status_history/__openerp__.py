# -*- coding: utf-8 -*-

{
    'name': 'Purchase Request Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of purchase request.
    """,
    'depends': [
        'document_status_history',
        'purchase_request',
    ],
    'demo': [],
    'data': [
        'data/purchase_request_history_rule.xml',
        'views/purchase_request_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
