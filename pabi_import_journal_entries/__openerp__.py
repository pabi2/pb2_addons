# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Bulk Import Journal Entries",
    "summary": "",
    "version": "1.0",
    "category": "Accounting & Finance",
    "description": """

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "pabi_account_move_adjustment",
    ],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/pabi_import_journal_entries_view.xml",
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
