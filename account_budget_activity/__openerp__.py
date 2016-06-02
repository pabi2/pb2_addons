# -*- coding: utf-8 -*-
{
    'name': 'Activity Based Budgets Management',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """

Activity based budgetting

Testing:
* Make sure that, activity_group_id, activity_id is passed from
  PR -> Call for Bid -> PO
  PR -> PO
* Make sure when confirm PR, Call for Bid, PO, Invoice, the Analyic is created
    2 types 1) product, 2) activity

""",
    'author': 'Kitti U.',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'account',
        'account_accountant',
        'account_move_line_doc_ref',
        'purchase',
        'purchase_requisition',
        'purchase_request',
        'purchase_request_to_requisition',
        'purchase_qty_invoiced_received',
        'hr_expense',
        'hr_expense_auto_invoice',
    ],
    'data': [
        'data/account_data.xml',
        'data/budget_release_cron.xml',
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'wizard/budget_release_wizard_view.xml',
        'views/purchase_view.xml',
        'views/purchase_requisition_view.xml',
        'views/purchase_request_view.xml',
        'views/account_budget_view.xml',
        'views/account_activity_view.xml',
        'views/purchase_view.xml',
        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/account_move_line_view.xml',
        'views/analytic_view.xml',
        'views/hr_expense_view.xml',
        'views/account_journal_view.xml',
        'wizard/purchase_request_line_make_purchase_requisition_view.xml',
        'workflow/account_budget_workflow.xml',
        'report/budget_consume_report_view.xml',
        'report/budget_plan_report_view.xml',
        'report/budget_monitor_report_view.xml',
    ],
    'demo': [
        'demo/activity_demo.xml',
        'demo/account_budget_demo.xml',
        'demo/purchase_request_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
