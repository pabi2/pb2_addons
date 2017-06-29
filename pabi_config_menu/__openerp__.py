# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSTDA :: PABI2 - Menu",
    "summary": "Rearragne Menu Order for NSTDA",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "description": """

Menu or Purchase/Purchase
=========================

* Purchase Requests
* Purchase Request Lines
* Call for Bids
* Requests for Quotation
* Purchase Order
* Suppliers

Mass Editing
============

* Edit Custom/Partner Flag in Partner window

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitit U.,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "purchase",
        "purchase_requisition",
        "purchase_request",
    ],
    "data": [
        "data/menu_data.xml",
        "data/res_partner_mass_editing_data.xml",
    ],
}
