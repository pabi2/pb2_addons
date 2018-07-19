# -*- coding: utf-8 -*-
{
    'name': "NSTDA :: PABI2 Account - Budget/Account Chart Field",
    'summary': "",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '8.0.1.0.0',
    'depends': [
        'pabi_base',
        'account_budget_activity',  # <-- the main module
        # 'account',
        # 'sale',
        # 'purchase',
        # 'purchase_requisition',
        # 'purchase_request',
        'stock_request',
        'auditlog',
        # 'account_model_generate_hook',
    ],
    'data': [
        'security/security.xml',
        'security/security_rules_job_order.xml',
        'security/security_rules_chartfield_budget.xml',
        # 'security/security_rules_chartfield_operations.xml',  NO NEED
        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'data/cost_control_data.xml',
        'data/job_order_history_rule.xml',
        'wizard/stock_change_product_qty_view.xml',
        'views/account_budget_view.xml',
        'views/account_invoice_view.xml',
        'views/analytic_view.xml',
        'views/chartfield_view.xml',
        'views/hr_expense_view.xml',
        'views/hr_salary_view.xml',
        'views/account_move_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/purchase_request_view.xml',
        'views/purchase_requisition_view.xml',
        'views/purchase_request_line_make_purchase_requisition_view.xml',
        'views/stock_request_view.xml',
        'views/account_view.xml',
        'views/res_fund_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
