# -*- coding: utf-8 -*-
{
    "name": "Stock - Stock Request Reject Reason",
    "summary": "Module summary",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

Stock - Stock Request Reject Reason
======================================

  * When rejecting the stock request, user has to specify the reason.

    """,
    "website": "http://ecosoft.co.th",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_request",
    ],
    "data": [
        "wizard/reject_reason_view.xml",
        "views/stock_request_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
