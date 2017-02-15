# -*- coding: utf-8 -*-

{
    'name': "PND3, PND53 Forms",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'l10n_th_account',
        'hr',
        'resource',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/print_pnd_form_wizard.xml',
        'data/report_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
