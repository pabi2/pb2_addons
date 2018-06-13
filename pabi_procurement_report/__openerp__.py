# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Procurement Report',
    'version': '8.0.1.0.0',
    'category': 'Purchase',
    'description': """
""",
    'author': 'Ecosoft',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'report_xls',
        'pabi_procurement',
        'pabi_purchase_work_acceptance',
        'pabi_asset_management',
        'pabi_purchase_contract',
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/pabi_purchase_summarize_report_wizard.xml',
        # Created using pabi_utils xlsx_template
        'reports/xlsx_report_pabi_purchase_summarize.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
