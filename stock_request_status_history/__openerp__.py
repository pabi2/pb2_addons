# -*- coding: utf-8 -*-

{
    'name': 'Stock Request Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of purchase requisition.
    """,
    'depends': [
        'document_status_history',
        'stock_request',
    ],
    'demo': [],
    'data': [
        'data/stock_request_history_rule.xml',
        'views/stock_request_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
