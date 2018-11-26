# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Easy Stock Transfer",
    "summary": "Easy Stock Enhancement",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
    "description": """

Miscellenous enhancement about easy stock transfer.

* Allow selecting all products, not only those availableself.
* Aloow stock in and out manually

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_easy_internal_transfer",
        "stock_operating_unit",
        "stock_picking_cancel"
    ],
    "data": [
        "views/stock_view.xml",
        "views/product_view.xml",
        "views/stock_valuation_history_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
