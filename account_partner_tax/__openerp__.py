# -*- coding: utf-8 -*-
{
    'name': 'Account Partner Tax',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Allow setup default taxes on partner',
    'description': """

This module allow setup default taxes in partner. It will merge partner taxes
with product taxes when user work on product line.

Available on: Sales Order, Purchase Order and Invoices

    """,
    'author': "Ecosoft",
    'website': 'http://www.ecosoft.co.th/',
    'depends': [
        'account',
        'sale',
        'purchase',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'application': True,
}
