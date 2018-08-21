# -*- coding: utf-8 -*-
{
    'name': 'Account Asset Report',
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
        'pabi_asset_management',
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/menu_asset.xml',
        'reports/asset_repair_report.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
    ],
}
