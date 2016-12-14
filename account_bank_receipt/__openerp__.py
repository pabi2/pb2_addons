# -*- coding: utf-8 -*-
{
    'name': 'Account Bank Receipt',
    'version': '8.0.0.1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Manage trasfer from intransit account the bank',
    'author': "Ecosoft",
    'website': 'http://www.ecosoft.co.th/',
    'depends': [
        'account_accountant',
        'report_webkit',
    ],
    'data': [
        'data/account_bank_receipt_sequence.xml',
        'data/account_data.xml',
        'wizard/voucher_create_bank_receipt_wizard.xml',
        'views/account_config.xml',
        'views/account_bank_receipt_view.xml',
        'views/account_move_line_view.xml',
        'views/account_view.xml',
        'views/account_voucher_view.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/report_bank_receipt.xml',
    ],
    'installable': True,
    'application': True,
}
