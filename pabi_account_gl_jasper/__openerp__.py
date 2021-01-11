# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: Account GL Jasper',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
""",
    'author': 'Peerapol C.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'pabi_account_report',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/jasper_data.xml',
        'reports/jasper_report_journal_document_entry.xml',
        'reports/jasper_asset_register_report.xml',
        'reports/jasper_report_gl_project.xml',
        'reports/jasper_report_expense_ledger.xml',
        'reports/jasper_report_revenue_ledger.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
