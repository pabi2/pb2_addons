# -*- coding: utf-8 -*-

{
    'name': 'Document Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of documents.
    """,
    'depends': [
        'auditlog',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/document_history.xml',
        'views/auditlog_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
