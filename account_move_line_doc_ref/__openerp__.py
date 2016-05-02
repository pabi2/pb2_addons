# -*- coding: utf-8 -*-
{
    'name': 'Account Move Line - Doc Ref',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'summary': 'Account Move Line - Doc Ref',
    'description': """
Account Move Line - Doc Ref
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'account_reversal',
        'account_asset',
        'account_voucher',
        'account_check_deposit',
        'stock_account',
    ],
    'demo': [],
    'data': [
        'views/account_move_line_view.xml',
        'views/account_voucher_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
