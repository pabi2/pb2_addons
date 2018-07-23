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
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_auto_vacumm.xml',
        'wizard/budget_drilldown_report_wizard.xml',
        'views/budget_drilldown_common.xml',
        'views/budget_overall_report.xml',
        'views/budget_unit_base_report.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
