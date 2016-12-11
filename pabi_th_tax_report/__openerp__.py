# -*- coding: utf-8 -*-

{
    'name': "PABI2 Thai Tax Report",
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'description': """

Add taxbranch criteria
""",
    'author': "Kitti U.",
    'website': 'http://ecosoft.co.th',
    'license': 'AGPL-3',
    "depends": [
        'l10n_th_tax_report',
    ],
    "data": [
        'wizard/tax_report_wizard.xml',
        'report_data.xml',
    ],
    'test': [
    ],
    "demo": [],
    "active": True,
    "installable": True,
}
