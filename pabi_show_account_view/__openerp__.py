# -*- coding: utf-8 -*-
{
    'name': 'PABI :: Show Account View',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Hidden',
    'description': """
    """,
    'website': 'https://ecosoft.co.th/',
    'author': 'Tharathip C.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'pabi_apps_config',
        'pabi_account_financial_report_webkit',
        'account_journal_report_xls',
    ],
    'data': [
        'wizard/pabi_show_account_view.xml',
    ],
}
