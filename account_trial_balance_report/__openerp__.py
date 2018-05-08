# -*- coding: utf-8 -*-
{
    'name': 'Trial Balance (web)',
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
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/report_auto_vacumm.xml',
        'wizard/trial_balance_wizard.xml',
        'views/trial_balance_report.xml',
    ],
}
