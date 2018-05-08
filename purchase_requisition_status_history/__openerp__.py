# -*- coding: utf-8 -*-

{
    'name': 'Purchase Requisition Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of purchase requisition.
    """,
    'depends': [
        'document_status_history',
        'purchase_requisition',
    ],
    'demo': [],
    'data': [
        'data/purchase_requisition_history_rule.xml',
        'views/purchase_requisition_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
