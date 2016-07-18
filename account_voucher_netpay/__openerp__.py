# -*- coding: utf-8 -*-
{
    'name': 'Account Voucher NetPay',
    'version': '1.0',
    'author': 'Ecosoft',
    'website': 'http://www.ecosoft.co.th',
    'category': 'Ecosoft Custom',
    'summary': "Voucher Payment that merge customer and supplier",
    'description': """
Voucher Payment that merge customer and supplier.
Can be used instead of Customer Payment and Supplier Payment in order to Net AR/AP
    """,
    'data': [
        'views/account_voucher_view.xml',
    ],
    'depends': [
        'account_voucher',
        'l10n_th_account',
        'account_voucher_action_move_line_create_hooks',
    ],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
