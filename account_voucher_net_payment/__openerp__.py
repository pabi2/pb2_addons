# -*- coding: utf-8 -*-

{
    'name': 'Allow Net Payment in Account Voucher',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """

Option in creating Customer Payment and Supplier Payment, to allow net payment.

    """,
    'depends': ['account_voucher',
                'account_invoice_create_payment',
                ],
    'demo': [],
    'data': ['wizard/invoices_create_payment_wizard.xml',
             'views/voucher_payment_receipt_view.xml',
             ],
    'auto_install': False,
    'installable': True,
}
