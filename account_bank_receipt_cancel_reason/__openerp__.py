# -*- coding: utf-8 -*-

{
    'name': 'Bank Receipt Cancel Reason',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When an bank receipt is canceled, a reason must be given as text.
    """,
    'depends': ['account_bank_receipt'],
    'demo': [],
    'data': [
        'wizard/cancel_reason_view.xml',
        'view/account_bank_receipt_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
