# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - POS Order",
    "summary": "",
    "version": "1.0",
    "category": "Sales",
    "description": """

This module use sale_automatic_workflow for sales order of type POS.

When set automatic workflow = POS, the order will automatically,
* Create and Validate Invoice
* Create and Transfer Shipment
* Create and Pay Paymnet
    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_automatic_workflow",
        "pabi_chartfield",
        "pabi_utils",
        "pabi_account",
        "pabi_stock_easy_internal_transfer",
        "account_tax_force_rounding_method",
    ],
    "data": [
        "views/product_view.xml",
        "views/sale_view.xml",
        "views/sale_workflow_process_view.xml",
        "reports/xlsx_report_supplier_consignment.xml",
        "xlsx_template/xlsx_import_wizard.xml",
        "xlsx_template/templates.xml",
        "xlsx_template/load_template.xml",
    ],
    # "pre_init_hook": "pre_init_hook",  # Keeps the job running for now.
}
