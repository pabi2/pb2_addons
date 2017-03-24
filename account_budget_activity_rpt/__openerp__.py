# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Reporting Activity",
    "summary": "Add new dimension for reporting purpose",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

Additional Chartfields for Reporting Purposes

* report_activity_id

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_budget_activity",
    ],
    "data": [
        "wizard/purchase_request_line_make_purchase_requisition_view.xml",
        "views/account_invoice_view.xml",
        "views/account_move_line_view.xml",
        "views/analytic_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_requisition_view.xml",
        "views/purchase_view.xml",
        "views/sale_view.xml",
        "report/budget_consume_report_view.xml",
        "report/budget_monitor_report_view.xml",
        "report/budget_plan_report_view.xml",
    ],
}
