# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Budget Summary Report',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Tharathip C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'report_xls',
        'account_budget_activity',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/budget_summary_action_excel_export_wizard.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
