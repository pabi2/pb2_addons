# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "NSTDA :: PABI2 - Sequence Preprint",
    "summary": "New sequence by month instead pre-print",
    "version": "8.0.1.0.0",
    "category": "Hidden",
    "description": """
        Adapt sequence from odoo v13 to v8
    """,
    "website": "http://ecosoft.co.th",
    "author": "Ecosoft, Odoo SA",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base"],
    "data": [
        "data/account_data.xml",
        "views/ir_sequence_preprint_views.xml",
    ],
}
