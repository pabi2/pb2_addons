# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 - Purchase Cash on Delivery',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Allow shipment process only after invoice is fully paid',
    'description': """

New invoice method for purchase, Before Delivery, is added. If this option is
selected, user won't be able to process shipment (will be blocked).

    """,
    'category': 'Purchase',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'purchase',
        'account',
    ],
    'demo': [],
    'data': [
        'data/payment_term_data.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
