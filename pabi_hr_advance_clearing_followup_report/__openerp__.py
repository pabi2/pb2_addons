# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - HR Expense Advance Clearing - Followup Report",
    "summary": "HR Expense Advance Clearing.",
    "version": "8.0.1.0.0",
    "category": "Human Resources",
    "description": """

HR Expense Advance Clearing Followup report

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'hr_expense_advance_clearing',
    ],
    "data": [
        'report/advance_clearing_report_sql_view.xml',
        'wizard/advance_clearnig_wizard_view.xml',
    ],
}
