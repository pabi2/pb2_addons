# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 - Purchase Contract Reports',
    'version': '8.0.1.0.0',
    'category': 'Purchase',
    'description': """
""",
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'pabi_purchase_contract',
        'pabi_utils',
    ],
    'data': [
        'data/menu.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/load_template.xml',
        'reports/xlsx_report_purchase_contract.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
