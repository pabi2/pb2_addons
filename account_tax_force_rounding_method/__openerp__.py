# -*- coding: utf-8 -*-
{
    "name": "Allow force rounding method",
    "summary": "",
    "version": "1.0",
    "category": "Sales",
    "description": """
This is working with Sales Order -> Customer Invoice

* In sales order, there is a new field - force_tax_rounding_method
* If force_tax_rounding_method,
  this will be used as rounding method regardless of global setting
* For invoice, it will lookup to the this force method in sales order

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "l10n_th_account",
    ],
    "data": [
    ],
}
