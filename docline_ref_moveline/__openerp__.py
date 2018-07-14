# -*- coding: utf-8 -*-
{
    "name": "Document Line Ref to Account Move Line",
    "summary": "",
    "version": "1.0",
    "category": "Hidden",
    "description": """
When post a document, i.e., invoice, this module add document line reference
back to account.move.line. The intention of this module is for reporting.

  * ref_invoice_line_id
  * ref_stock_move_id (TODO)

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'account',
    ],
    "data": [
    ],
    "application": False,
    "installable": True,
}
