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
--------------------------

* Partner Dunning Report

    """,
    'depends': [
        'pabi_account',
    ],
    'data': [
        # Partner Dunning Report
        'pabi_partner_dunning_report/report_data.xml',
        'pabi_partner_dunning_report/wizard/pabi_partner_dunning_wizard.xml',
        'pabi_partner_dunning_report/wizard/print_partner_dunning_letter.xml',
        'pabi_partner_dunning_report/report/pabi_partner_dunning_report.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
