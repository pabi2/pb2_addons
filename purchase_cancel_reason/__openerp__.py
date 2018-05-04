# -*- coding: utf-8 -*-
# © 2015 TrinityRoots>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase - Purchase Order Cancel Reason",
    "summary": "Module summary",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

Purchase - Purchase Order Cancel Reason
======================================

  * When cancelling the purchase order, user has to specify the reason.

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
        "wizard/cancel_reason_view.xml",
        "views/purchase_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
