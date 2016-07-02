# -*- coding: utf-8 -*-

{
    'name': 'HR Expense Status History',
    'version': '1.0',
    'author': "Ecosoft",
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'images': [],
    'website': "http://ecosoft.co.th",
    'description': """
    Records the status history of expense.
    """,
    'depends': [
        'document_status_history',
        'hr_expense',
    ],
    'demo': [],
    'data': [
        'data/hr_expense_history_rule.xml',
        'views/hr_expense_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
