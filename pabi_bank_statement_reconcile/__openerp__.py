# -*- coding: utf-8 -*-

{
    'name': "NSTDA :: PABI2 - Bank Statment Reconcile",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',

    'description': """

This module find the discrepency between payment export (Cheque, DIRECT, SMART)
and result from bank statement

    """,
    'depends': [
        'pabi_account',
    ],
    'data': [
        'views/pabi_bank_statement_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
