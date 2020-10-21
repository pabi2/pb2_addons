# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Account Asset Jasper',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Waritchapat K.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'pabi_account_report',
    ],
    'data': [
#         'security/ir.model.access.csv',
        'reports/jasper_report_asset_inactive_owner.xml',
        'data/jasper_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
