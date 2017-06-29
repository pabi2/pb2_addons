# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of account invoices.
    """,
    'depends': [
        'document_status_history',
        'account',
    ],
    'demo': [],
    'data': [
        'data/account_invoice_history_rule.xml',
        'views/account_invoice_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
