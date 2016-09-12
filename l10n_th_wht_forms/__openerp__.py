# -*- coding: utf-8 -*-

{
    'name': "Thai WHT Forms",
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'description': """
Thai Vat Report
""",
    'author': "Kitti U.",
    'website': 'http://ecosoft.co.th',
    'license': 'AGPL-3',
    "depends": [
        'account_voucher',
        'l10n_th_account',
    ],
    "data": [
        'jasper_data.xml',
    ],
    'test': [
    ],
    "demo": [],
    "active": True,
    "installable": True,
}
