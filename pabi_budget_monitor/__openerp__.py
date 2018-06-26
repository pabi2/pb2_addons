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
        'account_budget_activity_rpt',
        'pabi_chartfield',
        'pabi_procurement',
        'pabi_account_move_document_ref',
        'pabi_budget_internal_charge',
    ],
    'data': [
        'security/ir.model.access.csv',
        # View
        'views/res_fund_view.xml',
        'views/res_org_structure_view.xml',
        'views/res_spa_structure_view.xml',
        'views/res_other_structure_view.xml',
        'views/account_budget_view.xml',
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
