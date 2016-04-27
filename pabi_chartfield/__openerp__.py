# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Account - Budget/Account Chart Field",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'pabi_base',
        'account_budget_activity',
        'account',
        'purchase',
        'purchase_requisition',
        'purchase_request',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cost_control_data.xml',
        'views/account_budget_view.xml',
        'views/account_invoice_view.xml',
        'views/analytic_view.xml',
        'views/chartfield_view.xml',
        'views/hr_expense_view.xml',
        'views/account_move_view.xml',
        'views/purchase_view.xml',
        'views/purchase_request_view.xml',
        'views/purchase_requisition_view.xml',
        'views/purchase_request_line_make_purchase_requisition_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
