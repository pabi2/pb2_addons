# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Budget Preparation Prev FY Extension",
    'summary': "Run prev fy from monitor report",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'pabi_budget_plan',
        'pabi_budget_monitor',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/budget_plan_invest_construction_view.xml',
        'views/budget_plan_project_view.xml',
        'views/budget_plan_unit_view.xml',
        'views/invest_asset_plan_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
