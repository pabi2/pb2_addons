# -*- coding: utf-8 -*-

{
    'name': 'Customer Invoice Cancel Reason',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When a customer invoice is canceled, a reason must be given as text.
    """,
    'depends': ['account'
                ],
    'demo': [],
    'data': ['wizard/cancel_reason_view.xml',
             'view/account_invoice_view.xml',
             ],
    'auto_install': False,
    'installable': True,
 }
