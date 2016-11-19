# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 - Purchase Cash on Delivery',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Allow shipment process only after invoice is fully paid',
    'description': """

New invoice method for purchase, Before Delivery, is added. If this option is
selected, user won't be able to process shipment (will be blocked) until
all invoice has been paid.

When invoice is validated, account will be posted to prepaid account instead
of normal product account.

When each shipment is transferred, additional dr/cr will be posted to clear
prepaid account with normal project account.

    """,
    'category': 'Purchase',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'purchase',
        'account',
        'account_invoice_action_move_create_hook',
    ],
    'demo': [],
    'data': [
        'data/account_data.xml',
        'data/payment_term_data.xml',
        'views/account_invoice_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
