# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Year End Process",
    'summary': "Carry forward budget to next year",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'pabi_budget_monitor',
        'pabi_chartfield_merged',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/budget_carry_over_view.xml',
        'views/project_balance_carry_forward_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
