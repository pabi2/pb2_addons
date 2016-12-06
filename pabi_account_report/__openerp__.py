# -*- coding: utf-8 -*-

{
    'name': "NSTDA :: PABI2 - Accounting Reports",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',

    'description': """

Expense Related Reports
=======================

* AR Late Payment Penalty

    """,
    'depends': [
        'pabi_account',
    ],
    'data': [
        'pabi_ar_late_payment_penalty/wizard/pabi_ar_late_payment_penalty.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
