# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 - Multi Deduction Chartfields',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'summary': 'Journal Entries Adjustmnet Doctypes',
    'description': """
This module add more chartfields in table mutiple deduction in account.voucher
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'l10n_th_account_deduction',
        'account_budget_activity',
        'pabi_chartfield',
    ],
    'demo': [],
    'data': [
        'views/account_voucher_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
