# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - HR Expense (AP/AV)",
    "summary": "",
    "version": "1.0",
    "category": "Human Resources",
    "description": """

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_web_config",
        "hr_expense_auto_invoice",
        "hr_expense_advance_clearing",
        "hr_expense_cancel_reason",
        "account_budget_activity",
        "l10n_th_account",
        "account_invoice_cancel_reason",
        "pabi_attachment_helper",
    ],
    "data": [
        "security/ir.model.access.csv",
        # 'workflow/hr_expense_workflow.xml',
        'wizard/expense_create_multi_supplier_invoice_view.xml',
        "wizard/hr_expense_change_advance_date_due_view.xml",
        'wizard/employee_message_view.xml',
        'wizard/open_apweb_ref_url_view.xml',
        "views/account_activity_view.xml",
        "views/hr_expense_view.xml",
        "views/account_invoice_view.xml",
        'wizard/expense_create_supplier_invoice_view.xml',
    ],
}
