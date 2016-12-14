# -*- coding: utf-8 -*-
{
    'name': 'Account Move - Document Ref',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'summary': 'Account Move - Document Ref',
    'description': """
Journal Entry's regerence to source document
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'account',
        'account_voucher',
        'account_bank_receipt',
        'stock_account',
        'purchase_cash_on_delivery',
        'pabi_interface',
        'pabi_budget_internal_charge',
    ],
    'demo': [],
    'data': [
        'views/account_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
