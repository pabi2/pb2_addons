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

To issue the receipt, user will come to invoice and do the payment manually.

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_automatic_workflow",
        "pabi_chartfield",
    ],
    "data": [
        "data/stock_data.xml",
        "data/automatic_workflow_data.xml",
        "views/sale_view.xml",
        "views/sale_workflow_process_view.xml",
    ],
}
