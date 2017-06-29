# -*- coding: utf-8 -*-

{
    'name': 'HR Expense Value Date',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When a supplier payment is validated it records
    the date history on related expense.
    """,
    'depends': [
        'l10n_th_fields',
        'hr_expense_auto_invoice',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_expense_view.xml',
        'views/account_voucher_view.xml',
        'wizard/change_value_date_wizard_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
