# -*- coding: utf-8 -*-

{
    'name': 'Purchase to Invoice by Percent',
    'version': '1.0',
    'author': 'Ecosoft',
    'category': 'Sales',
    'description': """

This module enhance the existing Create Invoice (Advance / Percentage)
concept of standard Odoo by 2 things,

Create Invoice by Percent
=========================

Ability to create invoice by percentage of completion. This is not the same as
existing "Percentage" method that using the whole net amount, instead,
it goes into each line of Sales Order to create new Invoice.

This result a real create invoice by percentage of completion.

In addition, it also allow user to use Amount instead of percent
(system will do the convert to percent).

    """,
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': ['purchase',
                ],
    'demo': [],
    'data': ['wizards/purchase_make_invoice_advance.xml',
             'views/purchase_view.xml',
             'views/account_invoice_view.xml',
             'views/account_config.xml',
             ],
    'test': [],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
