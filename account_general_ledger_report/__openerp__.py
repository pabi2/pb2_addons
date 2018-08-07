# -*- coding: utf-8 -*-
{
    'name': 'General Ledger (web)',
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
        'wizard/general_ledger_wizard.xml',
        'views/general_ledger_report.xml',
    ],
}
