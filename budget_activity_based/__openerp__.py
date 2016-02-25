# -*- coding: utf-8 -*-

{
    'name': "Budget by Activity Based",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'account_accountant',
        'account_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_activity_view.xml',
        'views/account_budget_view.xml',
        'views/analytic_view.xml',
        'views/account_move_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [
        'demo/activity_demo.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
