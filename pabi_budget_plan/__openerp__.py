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
        'document_status_history',
        'pabi_invest_construction',  # Budget Control will pull from
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/history_rule.xml',
        'wizard/cost_control_breakdown_wizard.xml',
        'wizard/convert_to_budget_control_wizard.xml',
        'wizard/asset_plan_to_budget_plan_wizard.xml',
        'wizard/invest_asset_select_wizard_view.xml',
        'views/budget_plan_menu.xml',
        'views/budget_plan_unit_view.xml',
        'views/budget_plan_project_view.xml',
        'views/budget_plan_personnel_view.xml',
        'views/budget_plan_invest_asset_view.xml',
        # 'views/budget_plan_invest_construction_view.xml',
        'view/budget_plan_invest_construction_view.xml',
        'views/budget_fiscal_policy_view.xml',
        'views/invest_asset_plan_view.xml',
        'views/account_budget_view.xml',
        'views/section_budget_transfer_view.xml',
        'views/report_section_budget_transfer_view.xml',
        'views/budget_plan_report.xml'
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
