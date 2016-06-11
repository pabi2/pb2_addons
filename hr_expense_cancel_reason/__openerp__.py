# -*- coding: utf-8 -*-

{
    'name': 'HR Expense Cancel Reason',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    When a hr expense is canceled, a reason must be given as text.
    """,
    'depends': [
        'hr_expense',
    ],
    'demo': [],
    'data': [
        'wizard/cancel_reason_view.xml',
        'views/hr_expense_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
