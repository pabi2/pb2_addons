# -*- coding: utf-8 -*-
{
    'name': 'Activity Based Budgets Management',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """

Activity based budgetting

Note: This module provide only framework. There will be no budget check here.

""",
    'author': 'Kitti U.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'account',
        'account_accountant',
        # 'account_move_line_doc_ref',
        'sale',
        'purchase',
        'purchase_requisition',
        'purchase_request',
        'purchase_request_to_requisition',
        'purchase_qty_invoiced_received',
        'sale_qty_invoiced',
        'hr_expense',
        'hr_expense_auto_invoice',
        'hr_salary',
        'stock',
    ],
    'data': [
        'data/account_data.xml',
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'wizard/budget_release_wizard_view.xml',
        'wizard/change_release_amount_view.xml',
        'wizard/budget_technical_close.xml',
        'views/budget_transition_view.xml',
        'views/purchase_view.xml',
        'views/purchase_requisition_view.xml',
        'views/purchase_request_view.xml',
        'views/account_budget_view.xml',
        'views/account_activity_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/account_move_line_view.xml',
        'views/analytic_view.xml',
        'views/hr_expense_view.xml',
        'views/hr_salary_view.xml',
        'views/stock_view.xml',
        'views/account_journal_view.xml',
        'wizard/purchase_request_line_make_purchase_requisition_view.xml',
        'report/budget_consume_report_view.xml',
        'report/budget_plan_report_view.xml',
        'report/budget_monitor_report_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
