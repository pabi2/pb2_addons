# -*- coding: utf-8 -*-
{
    'name': 'Account Bank Payment',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage trasfer from intransit account the bank',
    'author': "Ecosoft",
    'website': 'http://www.ecosoft.co.th/',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'data/account_bank_payment_sequence.xml',
        'data/account_data.xml',
        'wizard/voucher_create_bank_payment_wizard.xml',
        'views/account_config.xml',
        'views/account_bank_payment_view.xml',
        'views/account_move_line_view.xml',
        'views/account_view.xml',
        'views/account_voucher_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
