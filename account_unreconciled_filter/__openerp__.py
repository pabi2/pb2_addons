# -*- coding: utf-8 -*-
{
    'name': 'Account Unreconciled Filter',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Create search for profiles for unreconciled move lines',
    'author': 'Ecosoft',
    'website': 'http://www.ecosoft.co.th/',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_unreconciled_filter.xml',
        'wizard/move_open_unreconciled_items.xml',
    ],
    'installable': True,
    'application': False,
}
