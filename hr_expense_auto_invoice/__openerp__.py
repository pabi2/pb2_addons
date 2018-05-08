# -*- coding: utf-8 -*-
{
    "name": "HR Expense with auto invoice",
    "summary": "Auto create supplier invoice instead of expense journal.",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

HR Expense with auto invoice
============================

This module change the behaviour of how Expense's
Journal and Payment will be generated.

Standard HR Expense
-------------------
Employee fill in Expense, once validated, Journal will be created for
this the expense.
No invoice is created, only reconcilable journal entries
Accountant will use Supplier Invoice to pay to employee,
for that journal entries.

Problem
-------
* This won't work in case of taxation.
* Accountant must always pay to employee, can't pay to supplier
  (again, problem to do tax report)

This Module Features
--------------------
* Option to pay to either Supplier or Employee
* Both case will create Supplier Invoice,
  receiver can be either Supplier or Employee depend on the selection.
* Add tax fields in expense lines, user can choose any tax like in invoice.
* After approve HR Expense, new invoice will be created and validated
  (if expense is cancelled, invoice will be cancelled
* As soon as invoice is created, accountant will use
  Supplier Invoice to pay as normal.


    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_expense",
        "hr_expense_sequence",
    ],
    "data": [
        "wizards/expense_create_supplier_invoice_wizard.xml",
        "views/hr_expense_view.xml",
        "workflow/hr_expense_workflow.xml",
        'views/invoice_view.xml',
    ],
}
