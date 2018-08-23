# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Actions / Jobs for Automation",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """
This module contain following Server Actions.
To activate, go to Server Actions menu, and add it to model's menu

- AV: Action -> Paid

  - hr.expense.expense of type AV
  - Confirm AV -> Create Invoic -> Pay for invoice

- 1 PR -> 1 PO

  - purchase.request
  - Nee disconnect PABIWeb
  - Sample PR @ data/purchase.request.csv
  - Confirm PR -> Create Requisition -> Create Quotation -> Create PO

- 1 CFB -> 1 PO

  - purchase.requisition
  - disconnect PABIWeb
  - Confirm Requisition -> Create Quotation -> Create PO

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_hr_expense",
        "account_invoice_create_payment",
        "pabi_procurement",
        "pabi_budget_plan",
        "pabi_invest_construction",
    ],
    "data": [
        "data/server_action.xml",
        "wizards/auto_approve_invest_construction.xml",
    ],
}
