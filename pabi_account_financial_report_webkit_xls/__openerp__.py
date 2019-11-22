# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 - Add XLS export to accounting reports',
    'version': '8.0.0.4.0',
    'license': 'AGPL-3',
    'author': "Noviat,Ecosoft,Tharathip C.",
    'category': 'Generic Modules/Accounting',
    'description': """

    This module adds XLS export to the following accounting reports:
        - general ledger
        - trial balance
        - partner ledger
        - partner balance
        - open invoices

    """,
    'depends': [
        'report_xls',
        'pabi_account_financial_report_webkit',
    ],
    'demo': [],
    'data': [
        'wizard/general_ledger_wizard_view.xml',
        'wizard/trial_balance_wizard_view.xml',
        'wizard/partners_ledger_wizard_view.xml',
        'wizard/partners_balance_wizard_view.xml',
        'wizard/open_invoices_wizard_view.xml',
        'wizard/account_financial_report_wizard_view.xml',
    ],
    'test': [
        'tests/general_ledger.yml',
        'tests/partner_ledger.yml',
        'tests/trial_balance.yml',
        'tests/partner_balance.yml',
        'tests/open_invoices.yml',
    ],
    'active': False,
    'installable': True,
}
