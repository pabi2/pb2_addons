# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Stock Asset",
    "summary": "Pabi2 Stock Asset",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
    "description": """

PABI2 - Stock Asset
===================

  * Customize for generating asset serial number according to product category.
  * Use asset serial number as product lot for asset

    """,
    "website": "https://nstda.or.th/",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_asset",
        "purchase_requisition",
    ],
    "data": [
        # "wizards/stock_transfer_details_view.xml",
        "views/asset_view.xml",
        "views/product_view.xml",
        "views/purchase_requisition_view.xml",
        "views/stock_view.xml",
        "views/account_invoice_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
