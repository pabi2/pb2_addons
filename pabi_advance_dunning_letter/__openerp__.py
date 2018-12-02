# -*- coding: utf-8 -*-

{
    'name': "NSTDA :: PABI2 - Advance Dunning Report",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',

    'description': """

Expense Related Reports
=======================

* Dunning Report

    """,
    'depends': [
        'email_template_dateutil',
        'pabi_hr_expense',
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/dunning_sequence.xml',
        'data/report_data.xml',
        # 'edi/email_templates_-1_days.xml',
        'edi/email_templates_0_days.xml',
        'edi/email_templates_5_days.xml',
        'edi/email_templates_10_days.xml',
        'views/pabi_dunning_letter_view.xml',
        'views/account_config.xml',
        # Export Excel
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
        'xlsx_template/xlsx_template_wizard.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
