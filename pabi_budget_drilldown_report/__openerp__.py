# -*- coding: utf-8 -*-
{
    'name': 'Budget Drilldown Report',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """

    """,
    'website': 'https://ecosoft.co.th/',
    'author': 'Kitti U.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'pabi_budget_monitor',
        'pabi_utils',
        'pabi_my_project',
    ],
    'data': [
        'security/pabi_budget_drilldown_report_security.xml',
        'security/ir.model.access.csv',
        'data/report_auto_vacumm.xml',
        'wizard/budget_drilldown_report_wizard.xml',
        'views/budget_drilldown_common.xml',
        'views/budget_overall_report.xml',
        'views/budget_unit_base_report.xml',
        'views/budget_project_base_report.xml',
        'views/budget_invest_asset_report.xml',
        'views/budget_invest_construction_report.xml',
        'views/budget_personnel_report.xml',
        'views/analytic_view.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
