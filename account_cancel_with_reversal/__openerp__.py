# -*- coding: utf-8 -*-

{
    'name': 'Account Cancel With Reversal',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Create reverse entry on when invoice or voucher cancelled.',
    'description': """
It will create the reverse entry for invoice and voucher
when it cancelled.
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'account_reversal',
        'account_voucher_cancel_hooks',
        'account_invoice_cancel_hooks'
    ],
    'demo': [],
    'data': [
        'wizard/account_move_reverse_view.xml',
        'views/account_invoice_view.xml',
        'views/account_voucher_view.xml'
    ],
    'test': [
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
