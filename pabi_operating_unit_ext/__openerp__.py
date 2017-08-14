# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Extra Feature on OU",
    "summary": "All OU as required field",
    "version": "8.0.1.0.0",
    "category": "Generic Modules/Sales & Purchases",
    "author": "Ecosoft (Kitti U.)",
    "website": "http://ecosoft.co.th",
    "description": """

* Make OU required field.
* Enhance security, by only list OU user have access
* Access All Operating Unit option in Group and Operating Unit

    """,
    "depends": [
        # "account_budget_activity_operating_unit",
        "account_operating_unit",
        "account_voucher_operating_unit",
        "hr_expense_operating_unit",
        "operating_unit",
        "procurement_operating_unit",
        "purchase_operating_unit",
        "purchase_request_operating_unit",
        "purchase_request_procurement_operating_unit",
        "purchase_request_to_requisition_operating_unit",
        "purchase_requisition_operating_unit",
        "purchase_work_acceptance_operating_unit",
        "stock_account_operating_unit",
        "stock_operating_unit",
        "hr_expense_auto_invoice",  # passing OU from Expense to Invoice
        "sale_operating_unit",
        "sale_stock_operating_unit",
        "stock_request_operating_unit",
    ],
    "data": [
        "security/operating_unit_security.xml",
        "views/res_users_view.xml",
        "views/operating_unit_view.xml",
        "views/account_invoice_view.xml",
        "views/account_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
}
