# -*- coding: utf-8 -*-
# © 2015 TrinityRoots>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Purchase Request Extension",
    "summary": "Module summary",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

PABI2 - Purchase Request Extension
==================================

  * Add price comparison button to purchase requisition form.
  * Add description to 'Call for Bids' form.
  * Modified 'Call for Bids' form not to change product's description
    while changing product.

    """,
    "website": "https://nstda.or.th/",
    "author": "TrinityRoots",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_request_to_requisition",
    ],
    "data": [
        "views/purchase_requisition_view.xml",
    ],
}
