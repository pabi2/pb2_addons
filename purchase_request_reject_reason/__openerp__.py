# -*- coding: utf-8 -*-
# © 2015 TrinityRoots>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase - Purchase Request Reject Reason",
    "summary": "Module summary",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

Purchase - Purchase Request Reject Reason
======================================

  * When rejecting the purchase request, user has to specify the reason.

    """,
    "website": "http://www.trinityroots.co.th",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_request",
    ],
    "data": [
        "wizard/reject_reason_view.xml",
        "views/purchase_request_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
