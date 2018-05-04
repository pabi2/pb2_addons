# -*- coding: utf-8 -*-
{
    'name': 'Account Bank Receipt Deduction',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage trasfer from intransit account the bank deduction',
    'author': "Ecosoft",
    'website': 'http://www.ecosoft.co.th/',
    'depends': [
        'account_bank_receipt',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_bank_receipt_view.xml',
    ],
    'installable': True,
    'application': True,
}
