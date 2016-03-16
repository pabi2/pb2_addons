# -*- coding: utf-8 -*-
{
    'name': 'Account Voucher Payment Deductions',
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
    'depends': ['account_voucher_hook'],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
