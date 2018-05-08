# -*- coding: utf-8 -*-

{
    'name': "Thai Tax Report",
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'description': """

Thai Tax Report based on Tax Detail table

""",
    'author': "Kitti U.",
    'website': 'http://ecosoft.co.th',
    'license': 'AGPL-3',
    "depends": [
        'jasper_reports',
        'l10n_th_account_tax_detail',
    ],
    "data": [
        'security/ir.model.access.csv',
        'wizard/tax_report_wizard.xml',
        'report_data.xml',
    ],
    'test': [
    ],
    "demo": [],
    "active": True,
    "installable": True,
}
