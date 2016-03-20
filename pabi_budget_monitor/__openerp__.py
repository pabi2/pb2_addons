# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Budget Monitor (based on chartfields)",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': ['pabi_chartfield',
                ],
    'data': [
        'views/account_view.xml',
        'views/res_org_structure_view.xml',
        'views/res_spa_structure_view.xml',
        #'report/account_analytic_entries_report_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
