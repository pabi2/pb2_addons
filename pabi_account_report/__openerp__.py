# -*- coding: utf-8 -*-

{
    'name': "NSTDA :: PABI2 - Accounting Reports",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',

    'description': """

Accounting Related Reports
==========================

* Customer Dunning Report

    """,
    'depends': [
        'pabi_hr_expense',
    ],
    'data': [
        'pabi_customer_dunning_report/report/pabi_customer_dunning_wizard.xml',
        'pabi_customer_dunning_report/report/pabi_customer_dunning_report.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
