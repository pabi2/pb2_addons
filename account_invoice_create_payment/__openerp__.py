# -*- coding: utf-8 -*-

{
    'name': 'Create Payment from Selected Invoices',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """

Allow select multiple invoice in tree view to create payment using action.
The payment will ensure that only selected invoice will be listed.

    """,
    'depends': ['account_voucher',
                ],
    'demo': [],
    'data': ['wizard/invoices_create_payment_wizard.xml',
             ],
    'auto_install': False,
    'installable': True,
}
