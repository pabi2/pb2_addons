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
        # View
        'views/res_org_structure_view.xml',
        'views/res_spa_structure_view.xml',
        'report/budget_consume_report_view.xml',
        'report/budget_plan_report_view.xml',
        'report/budget_monitor_report_view.xml',
        'report/budget_monitor_report_wizard_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
