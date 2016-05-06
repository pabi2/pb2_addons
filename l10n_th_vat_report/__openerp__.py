# -*- coding: utf-8 -*-

{
    'name': "Thai Vat Report",
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'description': """
Thai Vat Report
""",
    'author': "Kitti U.",
    'website': 'http://ecosoft.co.th',
    'license': 'AGPL-3',
    "depends": [
        'account',
        'l10n_th_account'
    ],
    "data": [
        'wizard/vat_report_wizard_view.xml',
        'views/report_view.xml',
        'views/report.xml',
    ],
    'test': [
    ],
    "demo": [],
    "active": True,
    "installable": True,
}
