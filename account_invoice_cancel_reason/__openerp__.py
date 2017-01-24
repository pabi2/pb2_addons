# -*- coding: utf-8 -*-

{
    'name': 'Invoice Cancel Reason',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When an invoice is canceled, a reason must be given as text.
    """,
    'depends': ['account',
                'account_cancel',
                ],
    'demo': [],
    'data': ['wizard/cancel_reason_view.xml',
             'view/account_invoice_view.xml',
             ],
    'auto_install': False,
    'installable': True,
}
