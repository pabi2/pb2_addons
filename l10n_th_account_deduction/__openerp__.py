# -*- coding: utf-8 -*-
{
    'name': 'Account Voucher Payment Multiple Deductions',
    'version': '1.0',
    'author': 'Ecosoft',
    'website': 'http://www.ecosoft.co.th',
    'category': 'Ecosoft Custom',
    'description': """
Multiple Deductions on Voucher Payment.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/account_voucher_view.xml',
    ],
    'depends': [
        'l10n_th_account',
        'account_voucher_writeoff_move_line_get_hooks',
        'account_voucher_action_move_line_create_hooks',
    ],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
