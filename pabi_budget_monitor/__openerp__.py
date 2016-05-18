# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Budget Monitor (based on chartfields)",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'account_budget_activity',
        'pabi_chartfield',
        'pabi_procurement',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'data/account.activity.tag.csv',
        # 'data/account.activity.group.csv',
        #  'data/account.activity.csv',
        #  View
        'views/account_activity_view.xml',
        'views/res_org_structure_view.xml',
        'views/res_spa_structure_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
