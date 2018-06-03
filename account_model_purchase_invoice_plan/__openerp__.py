# -*- coding: utf-8 -*-
{
    'name': "Account Model from Purchase Invoice Plan",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'description': """

To create recurring entries from open invoice plan

    """,
    'version': '0.1.0',
    'depends': [
        'account',
        'account_subscription_enhanced',
    ],
    'data': [
        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/product_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
