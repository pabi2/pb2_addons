# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Budget Report',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'report_xls',
        'account_budget_activity',
        'pabi_budget_plan',
        'pabi_budget_monitor',
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'archive/wizards/budget_plan_unit_analysis_report_wizard.xml',
        # 'archive/wizards/budget_plan_project_analysis_report_wizard.xml',
        'wizards/budget_summary_report_wizard.xml',
        'wizards/budget_cost_centre_report_wizard.xml',
        'wizards/budget_detail_report_wizard.xml',
        # Created using pabi_utils xlsx_template
        'reports/xlsx_report_budget_plan_unit_analysis.xml',
        'reports/xlsx_report_budget_plan_project_analysis.xml',
        'reports/xlsx_report_budget_plan_personnel_analysis.xml',
        'reports/xlsx_report_asset_item_plan_analysis.xml',
        'reports/xlsx_report_budget_plan_asset_analysis.xml',
        'reports/xlsx_report_budget_plan_construction_analysis.xml',
        'reports/xlsx_report_budget_summary.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
