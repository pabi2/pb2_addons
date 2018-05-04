# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Merged Chartfield to 1 column",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '8.0.1.0.0',
    'depends': [
        'pabi_chartfield',
        'pabi_invest_construction',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/chartfield_view.xml',
        'views/hr_expense_view.xml',
        'views/hr_salary_view.xml',
        'views/purchase_request_line_make_purchase_requisition_view.xml',
        'views/purchase_request_view.xml',
        'views/purchase_requisition_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
