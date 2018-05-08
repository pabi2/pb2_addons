# -*- coding: utf-8 -*-

{
    'name': 'Payment Cancel Reason',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When an payment is canceled, a reason must be given as text.
    """,
    'depends': [
        'account_voucher'
    ],
    'demo': [],
    'data': [
        'wizard/cancel_reason_view.xml',
        'view/account_voucher_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
