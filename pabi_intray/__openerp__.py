# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Intray",
    "summary": "",
    "version": "1.0",
    "category": "Hidden",
    "description": """
This module contain helper function to post message as subtype intray.
So, intray system can watch and/or post message to portal.

It also contain defined message for following modules,

  - Stock Request

Odoo will provide view for other system to call as - pabi_intray_view

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'mail',
        'stock_request',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/message_subtype.xml',
        'data/stock_request_message.xml',
        'data/budget_transfer_message.xml',
    ],
    "application": False,
    "installable": True,
}
