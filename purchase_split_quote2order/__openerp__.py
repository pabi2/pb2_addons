# -*- coding: utf-8 -*-
# © 2015 TrinityRoots>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase - Separate Quote and Order",
    "summary": "Module summary",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

Purchase - Separate Quote and Order
===================================

  * Separate 'Request for Quotation' record to 'Purchase Order' record while
    confirming order.

    """,
    "website": "http://www.trinityroots.co.th",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase",
    ],
    "data": [
        "data/purchase_sequence.xml",
        "data/purchase_workflow.xml",
        "views/purchase_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
