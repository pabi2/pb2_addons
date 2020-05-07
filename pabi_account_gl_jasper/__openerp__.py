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
        'reports/jasper_report_journal_document_entry.xml',
        'data/jasper_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
