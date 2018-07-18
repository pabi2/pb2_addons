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
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_auto_vacumm.xml',
        'wizard/budget_drilldown_report_wizard.xml',
        'views/budget_drilldown_report.xml',
    ],
}
