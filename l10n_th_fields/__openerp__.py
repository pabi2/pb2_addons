# -*- coding: utf-8 -*-

{
    'name': 'Account Common Fields',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Additional useful field in accounting module.',
    'description': """

    """,
    'category': 'Accounting & Finance',
    'sequence': 4,
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': ['account_voucher'],
    'demo': [],
    'data': [
        'views/voucher_payment_receipt_view.xml',
        'views/partner_view.xml',
        'views/account_bank_view.xml',
        'views/account_invoice_view.xml',
        'views/ir_sequence_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
