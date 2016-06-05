# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Budget Preparation",
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
        'wizard/cost_control_breakdown_wizard.xml',
        'views/budget_plan_menu.xml',
        'views/budget_plan_project_view.xml',
        'views/budget_plan_unit_view.xml',
        'views/budget_fiscal_policy_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
