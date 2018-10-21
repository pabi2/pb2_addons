# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 - Partner Dunning Report",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',

    'description': """

    """,
    'depends': [
        'pabi_account',
    ],
    'data': [
        # Partner Dunning Report
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'data/report_data.xml',
        'report/qweb_report_customer_dunning_letter_template.xml',
        'report/layouts.xml',
        'views/pabi_partner_dunning_report.xml',
        'views/pabi_partner_dunning_letter_view.xml',
        'views/pabi_dunning_config.xml',
        'wizard/pabi_partner_dunning_wizard.xml',
        'wizard/create_dunning_letter.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
